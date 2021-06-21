import psycopg2
from elasticsearch import Elasticsearch, helpers
from load_test_data_to_postgres import DATABASE_CONFIG


ELASTICSEARCH_CONFIG = {
    'host': 'localhost',
    'port': 9200
}


if __name__ == "__main__":

    es = Elasticsearch(**ELASTICSEARCH_CONFIG)
    es.indices.create(index='posts')


    # retrieve and prepare data from postgres

    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    statement = "select id, document_text from document order by id"

    cursor.execute(statement)
    retrieved_data = cursor.fetchall()  # [[id, text], ... [id, text]]
    conn.close()


    def bulk_actions_gen(data):
        """generate dicts that describes document indexing action"""
        counter = 0
        bulk_actions = ({'_index': 'posts', '_id': document_id, '_source': {'iD': document_id, 'text': text}}
                        for document_id, text in data if data is not None)
        for action in bulk_actions:
            yield action
            counter += 1
        print(f'generated bulk actions for {counter} documents')


    bulk_indexing_gen = bulk_actions_gen(retrieved_data)
    helpers.bulk(es, bulk_indexing_gen)
