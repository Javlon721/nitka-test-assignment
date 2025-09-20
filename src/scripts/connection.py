from contextlib import contextmanager
from dataclasses import dataclass
import datetime
import os
import pathlib
import shutil
import sqlite3
from typing import TypedDict

from src.config import Config



class Publication(TypedDict):
    title: str
    summary: str
    tags: list[str]
    year_published: datetime
    organization: str
    country: str
    language: str
    pdf_link: str
    local_pdf_path: str
    authors: list[str]


def arr_to_str(data: list[any], delimiter: str = ', ') -> str:
    return delimiter.join([str(item) for item in data])

def dict_factory(cursor, row):
    fields = [column[0] for column in cursor.description]
    return {key: value for key, value in zip(fields, row) if value}

def custom_serialization(data: list[any]) -> list[str]:
    '''
        This fn can be definitly modified 
        so for simplicity and time consuption to solve this i make it redundantly
    '''
    result = []
    
    for value in data:
        new_value = None
        match value:
            case str():
                new_value = value
            case int():
                new_value = str(value)
            case list():
                new_value = arr_to_str(value)
            case datetime.datetime():
                new_value = str(value)
            case _:
                raise ValueError(f"Type {type(value)} is not implemented")

        result.append(new_value)

    return result

class Database:

    def __init__(self):
        self.db_file_path = Config.DATABASE_FILE_PATH
        self.db_link =  Config.DATABASE_LINK
        self.init_db()


    @contextmanager
    def get_connection(self):
        with sqlite3.connect(self.db_link) as conn:
            yield conn


    def init_db(self):
        try:
            self.create_db_folder()
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS publications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        summary TEXT,
                        authors TEXT NOT NULL,
                        tags TEXT,
                        year_published TIMESTAMP NOT NULL,
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
            self.create_db_folder()


    def create_db_folder(self):
        if self.is_db_exists():
            raise FileExistsError("DB data already exists")
        os.makedirs(self.db_file_path, exist_ok=True)


    def is_db_exists(self):
        return pathlib.Path.exists(self.db_file_path)


    def insert_publication(
        self, 
        data: Publication
):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            columns = arr_to_str(data.keys())
            values = custom_serialization(data.values())
            placeholders = arr_to_str(["?" for _ in values])

            query = 'INSERT INTO publications ({}) VALUES ({})'.format(columns, placeholders)
            cursor.execute(query, values)
            conn.commit()

            return cursor.lastrowid


    def get_publications(self, page=1, per_page=20):
        offset = (page - 1) * per_page
        
        with self.get_connection() as conn:
            conn.row_factory = dict_factory
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM publications')
            
            cursor.execute('''
                SELECT * FROM publications 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            ''', (per_page, offset))
            publications = cursor.fetchall()
            
            return publications




if __name__ == "__main__":
    test_db = Database()
    # test_data = Publication(
    #     title="Most popular",
    #     year_published=datetime.datetime.now(),
    #     tags=['tag1', 'tag2', 'tag3'],
    #     authors=['Author1', 'Author2']
    #     )
    # test_db.insert_publication(test_data)
    print(test_db.get_publications()[0])