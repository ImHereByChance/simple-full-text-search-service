import csv
import os
import psycopg2
from datetime import datetime


DATABASE_CONFIG = {
    'user':"postgres",
    'password': os.getenv('DATABASE_PASSWORD'),
    'host':"127.0.0.1",
    'port':"5432",
    'database':"posts"
}


if __name__ == "__main__":

    conn = psycopg2.connect(**DATABASE_CONFIG)
    cursor = conn.cursor()
    statement = """INSERT INTO document(created_date, document_text, rubrics_array)
                   VALUES(%s, %s, %s)"""

    with open('posts_example.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            processed_row = (datetime.fromisoformat(row['created_date']),
                             row['text'],
                             row['rubrics'])
            cursor.execute(statement, processed_row)
        conn.commit()

    conn.close()
