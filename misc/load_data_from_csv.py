""" Script for filling the database and Elasticsearch index with records from csv file"""


import asyncio
import asyncpg
import csv
from datetime import datetime
from elasticsearch import AsyncElasticsearch, helpers
from pathlib import Path
from pyaml_env import parse_config


LOCAL_CONFIG_FILE_PATH = Path(__file__).resolve().parent.parent / 'local_config.yaml'
DEFAULT_CONFIG_FILE_PATH = Path(__file__).resolve().parent.parent / 'source/default_config.yaml'
CSV_FILE_PATH = Path(__file__).resolve().parent / 'posts_example.csv'


def get_config():
    print('Loading configs...')
    try:
        config = parse_config(DEFAULT_CONFIG_FILE_PATH.as_posix())
        custom_config = parse_config(LOCAL_CONFIG_FILE_PATH.as_posix())
        if custom_config is not None:
            config.update(**custom_config)
    except:
        raise Exception('Cannot load default_config.yaml: it should be'
                      + 'placed in ./source dir OR local_config.yaml:'
                      + 'should be in project root dir')
    print('Done\n')
    return config


async def create_tables_and_indexes(db_config):
    print('Creating tables in database...')
    conn = await asyncpg.connect(**db_config)
    statement = """
        CREATE TABLE document (id SERIAL PRIMARY KEY,
                               created_date timestamp,
                               document_text text,
                               rubrics_array text);

        CREATE INDEX document_dates_desc_idx ON document(created_date); 
    """
    await conn.execute(statement)
    await conn.close()
    print('Done\n')


async def write_csv_in_db(db_config):
    print('Writing from csv file to database...')
    conn = await asyncpg.connect(**db_config)
    statement = """INSERT INTO document(created_date, document_text, rubrics_array)
                   VALUES($1, $2, $3)"""  
    with open(CSV_FILE_PATH, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            processed_row = (datetime.fromisoformat(row['created_date']),
                             row['text'],
                             row['rubrics'])
            await conn.execute(statement, *processed_row)
    await conn.close()
    print('Done\n')


async def bulk_actions_gen(data):
    """Generate dicts that describes document indexing action"""
    counter = 0
    bulk_actions = ({'_index': 'posts', '_id': document_id, '_source': {'iD': document_id, 'text': text}}
                    for document_id, text in data if data is not None)
    for action in bulk_actions:
        yield action
        counter += 1
    print(f'Generated bulk actions for {counter} documents.')


async def load_from_db_to_index(es_config, db_config):
    es = AsyncElasticsearch(**es_config)
    
    print('Creating index...')
    es.indices.create(index='posts')
    print('Done\n')

    conn = await asyncpg.connect(**db_config)
    statement = "select id, document_text from document order by id"

    print('Uploading data to Elasticsearch index...')
    retrieved_records = await conn.fetch(statement)
    await helpers.async_bulk(es, bulk_actions_gen(retrieved_records))
    print('Done\n')


async def main():
    print('\nStarting the script.\n')
    
    config = get_config()
    database_config = config['DATABASE_CONFIG']
    elastic_config = config['ELASTICSEARCH_CONFIG']

    await create_tables_and_indexes(database_config)
    await write_csv_in_db(database_config)
    await load_from_db_to_index(elastic_config, database_config)
    
    print('Finished.')


if __name__ == "__main__":
    asyncio.run(main())
