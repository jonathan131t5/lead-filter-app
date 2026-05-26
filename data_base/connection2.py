import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


class Connection:
    def __init__(self):
        database_url = os.getenv("DATABASE_URL")

        if not database_url:
            raise ValueError("DATABASE_URL is missing")

        self.conn = psycopg2.connect(database_url)
        self.cursor = self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def new_cursor(self):
        return self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()