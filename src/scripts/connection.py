from contextlib import contextmanager
import datetime
import os
import pathlib
import shutil
import sqlite3

from pydantic import BaseModel, Field

from src.config import Config


class PublicationLocation(BaseModel):
    pdf_link: str = ""
    local_pdf_path: str = ""


class Publication(PublicationLocation):
    title: str = ""
    summary: str = ""
    tags: list[str] = Field(default_factory=list)
    year_published:str = ""
    organization: str = ""
    country: str = ""
    language: str = ""


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
        self.table_name = "publications"


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
            self.create_db_folder()


    def create_db_folder(self):
        if self.is_db_exists():
            print("DB data already exists. Continue...")
            return
        os.makedirs(self.db_file_path, exist_ok=True)


    def is_db_exists(self):
        return pathlib.Path.exists(self.db_file_path)


    def insert_publication(
        self, 
        data: Publication
):
        with self.get_connection() as conn:
            print(f'Saving {data.title}')

            cursor = conn.cursor()
            to_save = data.model_dump()

            columns = arr_to_str(to_save.keys())
            values = custom_serialization(to_save.values())
            placeholders = arr_to_str(["?" for _ in values])

            query = 'INSERT INTO {} ({}) VALUES ({})'.format(self.table_name, columns, placeholders)
            cursor.execute(query, values)
            conn.commit()

            return cursor.lastrowid


    def insert_publications(self, data: list[Publication]):
        result = []

        for item in data:
            result.append(self.insert_publication(item)) #todo: remake db connections
        
        return result


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




if __name__ == "__main__":
    test_db = Database()
    test_data = Publication(
        title="Most popular",
        year_published='2202',
        tags=['tag1', 'tag2', 'tag3'],
        authors=['Author1', 'Author2'],
        )
    # test_db.insert_publication(test_data)
    print(test_db.get_publications())