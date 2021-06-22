from elasticsearch.client import indices
from source import dbase
import aiohttp
import json
import logging
from aiohttp import web


class AppConfigMixin:
    @property
    def dbase(self):
        return self.request.app['dbase']

    @property
    def elastic(self):
        return self.request.app['elastic']

    @property
    def app_logger(self):
        return self.request.app['loggers'].get('app_logger')


class IndexEndPoint(web.View):
    """ / """
    
    async def get(self):
        """GET /"""
        # TODO: return API documentation instead
        return web.json_response(data=self.request.app['config'])


class Search(web.View, AppConfigMixin):
    async def get(self):
        """GET /search?q=string%20for%20quering"""
        try:
            search_query = self.request.query['q']
            id_list = await self._make_req_to_elastic(search_query)
            search_results = await self.dbase.get_by_id_list(id_list)
            search_results_json = json.dumps(obj= {'results': search_results},
                                             ensure_ascii=False)
            return web.Response(body=search_results_json,
                                content_type='application/json')
        except KeyError:
            return web.json_response(data={'error': 'no search query suplied'},
                                     status=400)
        except:
            self.app_logger.exception('Exception during search.')
            return web.json_response(data={'error': 'internal server error'},
                                     status=500)

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
