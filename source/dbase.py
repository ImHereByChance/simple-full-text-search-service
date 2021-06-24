import asyncpg


class DBaseHandler():
    """ Object to handle database operations (selects and deletets)."""

    def __init__(self, dbase_config: dict) -> None:
        # a dict: { user: ... , password: ... , host: ... ,
        #           port: ... , database: ... }
        self.dbase_config = dbase_config

    async def get_by_id_list(self, id_list: list) -> list:
        """ Takes a list of identifiers (as ints) and returns a list of dicts,
        where dicts are the rows from the table that match the query.
        """
        if not id_list:
            return id_list

        conn = await asyncpg.connect(**self.dbase_config)
        records_list = await conn.fetch(
            """SELECT *
            FROM document
            WHERE id = ANY($1)
            ORDER BY created_date DESC""",
            id_list
        )
        await conn.close()
        dicts_list = [self._convert_record_to_serializable_dict(record)
                      for record in records_list]
        await conn.close()
        return dicts_list

    async def get_by_id(self, doc_id: int) -> dict:
        """ Takes id, returns the row with all its columns as a dict."""
        doc_id = int(doc_id)
        conn = await asyncpg.connect(**self.dbase_config)
        result = await conn.fetch("SELECT * FROM document where id = $1", doc_id)
        await conn.close()
        if result:
            dict_result = self._convert_record_to_serializable_dict(result[0])
            return dict_result
        else:
            return {}

    async def delete_by_id(self, doc_id: int) -> str:
        """ Delete a row by id."""
        doc_id = int(doc_id)
        conn = await asyncpg.connect(**self.dbase_config)
        statement = """DELETE FROM document where id = $1"""
        result_string = await conn.execute(statement, doc_id)
        await conn.close()
        return result_string

    async def row_exists(self, doc_id: int) -> bool:
        """ Returns True if row with given id exists in table."""
        doc_id = int(doc_id)
        statement = f"""select exists(select 123 from document where id = $1)"""
        conn = await asyncpg.connect(**self.dbase_config)
        results_list = await conn.fetch(statement, doc_id)
        await conn.close()
        return results_list[0]['exists']

    def _convert_record_to_serializable_dict(self, record: asyncpg.Record) -> dict:
        """ Takes asyncpg.Record object and converts it to a dict which
        can be serialized to a JSON (with str-dates and so on).
        """
        return {
            'id': record['id'],
            'created_date': record['created_date'].strftime("%Y-%d-%m %H:%M:%S"),
            'document_text': record['document_text'],
            'rubrics_array': eval(record['rubrics_array'])
        }
