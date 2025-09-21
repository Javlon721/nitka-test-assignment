import asyncio
from contextlib import contextmanager
import os
import shutil
import sqlite3

from src.scripts.db.models import PublicationInfo
from src.scripts.utils import arr_to_str, custom_serialization, print_shifts
from src.config import Config


def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row) if value}


class Database:

    def __init__(self, extracted_ch: asyncio.Queue[PublicationInfo] | None=None):
        self.db_file_path = Config.DATABASE_FILE_PATH
        self.db_link =  Config.DATABASE_LINK
        self.table_name = "publications"
        self.extracted_ch = extracted_ch or asyncio.Queue()

    @contextmanager
    def get_connection(self):
        with sqlite3.connect(self.db_link) as conn:
            yield conn


    def init_db(self):
        try:
            self.create_db_folder()
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        summary TEXT,
                        tags TEXT,
                        year_published TEXT,
                        organization TEXT,
                        country TEXT,
                        language TEXT DEFAULT 'English',
                        pdf_link TEXT,
                        local_pdf_path TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                conn.commit()
        except FileExistsError as e:
            print(e)


    def clear_db_folder(self):
        if self.is_db_exists():
            shutil.rmtree(self.db_file_path)


    def create_db_folder(self):
        if self.is_db_exists():
            print("DB data already exists. Continue...")
            return
        os.makedirs(self.db_file_path, exist_ok=True)


    def is_db_exists(self):
        return os.path.exists(self.db_file_path)


    def insert_publication(
        self, 
        data: PublicationInfo
):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            to_save = data.model_dump()

            columns = arr_to_str(to_save.keys())
            values = custom_serialization(to_save.values())
            placeholders = arr_to_str(["?" for _ in values])

            query = 'INSERT INTO {} ({}) VALUES ({})'.format(self.table_name, columns, placeholders)
            cursor.execute(query, values)
            conn.commit()

            print_shifts(f'Saved {data.title} to db')

            return cursor.lastrowid


    async def consumer(self):
        while True:
            data = await self.extracted_ch.get()
            if data == Config.END_VALUE_IN_CHANNELS:
                return

            self.insert_publication(data)


    def get_publications(self, page=1, per_page=20):
        offset = (page - 1) * per_page
        
        with self.get_connection() as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            
            cursor.execute(f'SELECT COUNT(*) FROM {self.table_name}')
            
            cursor.execute(f'''
                SELECT * FROM {self.table_name} 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            ''', (per_page, offset))
            publications = cursor.fetchall()
            
            return publications


    def get_publications_count(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM publications')
            return cursor.fetchone()[0]




if __name__ == "__main__":
    test_ch = asyncio.Queue()
    test_db = Database(test_ch)
    # test_data = Publication(
    #     title="Most popular",
    #     year_published='2202',
    #     tags=['tag1', 'tag2', 'tag3'],
    #     authors=['Author1', 'Author2'],
    #     )
    # test_db.insert_publication(test_data)
    print(len(test_db.get_publications()))