import json
from aiohttp import web

from elasticsearch.exceptions import NotFoundError
from .exceptions import FailToDeleteFromIndex, PartialDeletionError, IdNotDigitError


class AppConfigMixin:  # TODO: refactor this
    """A Mixin with shortcuts for self.request.app['...'] dict items"""

    @property
    def dbase(self):
        return self.request.app['dbase']

    @property
    def elastic(self):
        return self.request.app['elastic']

    @property
    def app_logger(self):
        return self.request.app['loggers'].get('app_logger')

    @property
    def partial_deletion_logger(self):
        return self.request.app['loggers'].get('partial_deletion_logger')


class IndexEndPoint(web.View):
    """ / """

    async def get(self):
        """GET /"""
        # TODO: return API documentation instead
        return web.json_response(data=self.request.app['config'])


class Post(web.View, AppConfigMixin):
    """Getting and deleting posts. """

    async def get(self):
        """GET /posts/:id"""

        try:
            # get and check id
            document_id = self.request.match_info['document_id']
            if not document_id.isdigit():
                raise IdNotDigitError(f'document id cannot be {document_id}')

            # get document from dbase
            result = await self.dbase.get_by_id(document_id)
            if result:
                json_result = json.dumps(dict(result), ensure_ascii=False)
                return web.json_response(body=json_result)
            else:
                error_dict = {'code': 404, 'message': 'document not found'}
                return web.json_response(data=error_dict, status=404)

        except IdNotDigitError:
            error_dict = {'code': 404,
                          'message': 'document not found or wrong type of id'}
            return web.json_response(data=error_dict, status=404)

        except:
            log_msg = ' Exception during hadeling request: {method} {path}'
            self.app_logger.exception(log_msg.format(method=self.request.method,
                                                     path=self.request.path))
            error_dict = {'code': 500, 'message': 'internal server error'}                                     
            return web.json_response(data=error_dict, status=500)

    async def delete(self):
        """DELETE /posts/:id"""

        try:
            # get and check id
            document_id = self.request.match_info['document_id']
            if not document_id.isdigit():
                raise IdNotDigitError(f'document id cannot be {document_id}')

            # delete from Elasticsearch index
            deletion_from_index_status = await self._delete_from_index(document_id)
            if deletion_from_index_status == 200:
                pass
            elif deletion_from_index_status == 404:
                error_dict = {'code': 404, 'message': 'document not found'}
                return web.json_response(data=error_dict, status=404)

            # delete from Postgres db
            await self._delete_from_db(document_id)

            # return message about successfull deletion
            success_resp_dict = {
                'code': 200,
                'message':f'document successfully deleted (id: {document_id})'
            }
            return web.json_response(data=success_resp_dict, status=200)

        except IdNotDigitError:
            error_dict = {'code': 404,
                          'message': 'document not found or wrong type of id'}
            return web.json_response(data=error_dict, status=404)

        except PartialDeletionError:
            self.partial_deletion_logger.exception(document_id)
            error_dict = {'code': 500,
                          'message': 'failed to delete: internal server error'}
            return web.json_response(data=error_dict, status=500)

        except:
            log_msg =f'Failed to delete document with id:{document_id}'
            self.app_logger.exception(log_msg)

            error_dict = {'code': 500, 
                          'message': 'failed to delete: internal server error'}
            return web.json_response(data=error_dict, status=500)

    async def _delete_from_index(self, document_id: int) -> int:
        """ Takes a document id and removes it from the Elasticsearch
        index. Returns 200 if succeeded, 404 if document with the
        suplied id does not exist in index or raises
        FailToDeleteFromIndex if something went wrong during deletion.
        """

        try:
            response = await self.elastic.delete(index='posts', id=document_id)
            if response['result'] == 'deleted':
                status_code = 200
            else:
                raise FailToDeleteFromIndex(document_id)
        except NotFoundError:  # response status 404
            status_code = 404
            try:
                # To avoide situations when a document with given id
                # exists in database, but don't in Elastic index.
                # Delete the inconsistent data from the db anyway and
                # log this.
                if await self.dbase.row_exists(document_id):
                    await self.dbase.delete_by_id(document_id)
                    log_msg = f"There was a document with id {document_id} "\
                              + "in DB but not in index"
                    self.app_logger.warning(log_msg)
            except:
                self.partial_deletion_logger.exception(
                    f'{document_id} (presumably)'
                )

        return status_code

    async def _delete_from_db(self, document_id: int) -> str:
        """ Deletes a document from the database by id. On failure,
        calls PartialDeletionError, which means that the document was
        deleted from the elastic index, but not from the database,
        and the two storages are not consistent. 
        """
        try:
            delete_conformation_string = await self.dbase.delete_by_id(document_id)

            # `True` means that we have successfully deleted a document by id
            # Elastic, but there is no row with such id in Postgres. Now the
            # data in both storages seems to be consistent, but perhaps we
            # need to figure out why this happened
            if delete_conformation_string == 'DELETE 0':
                log_msg = f"There was a document with id: {document_id} "\
                          + "in index but not in DB"
                self.app_logger.warning(log_msg)
            return 'ok'
        except:
            raise PartialDeletionError(document_id)


class Search(web.View, AppConfigMixin):
    """ Endpoint for full text search in documents.
    Searches through Elasticsearch index and returns matched documents
    with additional metadata from the database.
    """
    async def get(self):
        """GET /posts/search?q=string%20for%20quering"""
        try:
            search_query = self.request.query['q']
            id_list = await self._make_req_to_elastic(search_query)
            search_results = await self.dbase.get_by_id_list(id_list)
            search_results_json = json.dumps(obj={'results': search_results},
                                             ensure_ascii=False)
            return web.Response(body=search_results_json,
                                content_type='application/json')
        except KeyError:
            error_dict = {'code': 400, 'message': 'no search query suplied'}
            return web.json_response(data=error_dict, status=400)
        except:
            self.app_logger.exception('Exception during search.')
            error_dict = {'code': 500, 'message': 'internal server error'}
            return web.json_response(data=error_dict, status=500)

    async def _make_req_to_elastic(self, query_string: str) -> list:
        """Search through documents in the ElasticSearch index.
        Takes a query_string:str and return a list of IDs of the
        matched documents.
        """
        search_query_dict = {
            "query": {
                "query_string": {
                    "query": query_string
                }
            },
            "fields": ["iD"],
            "size": 20
        }

        hits_dict = await self.elastic.search(
            index='posts',
            body=search_query_dict,
            filter_path=['hits.hits._source.iD']
        )

        if hits_dict:
            id_list = [dct['_source']['iD']
                       for dct in hits_dict['hits']['hits']]
            return id_list
        else:
            return []
