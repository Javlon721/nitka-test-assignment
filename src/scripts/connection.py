from contextlib import contextmanager
import datetime
import os
import pathlib
import shutil
import sqlite3

from src.config import Config

class Database:
    def __init__(self, db_name: str):
        self.db_path = Config.DATABASE_PATH
        self.db_name = db_name
        self.init_db()

    @property
    def db_link(self):
        return pathlib.Path(self.db_path, self.db_name)

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
        except FileExistsError:
            print("DB data already exists")
    
    def clear_db_folder(self):
        shutil.rmtree(self.db_path)
        self.create_db_folder()
    
    def create_db_folder(self):
        os.makedirs(self.db_path, exist_ok=True)

    def insert_publication(
        self, 
        title: str,
        summary: str,
        tags: str,
        year_published: datetime,
        organization: str,
        country: str,
        language: str,
        pdf_link: str,
        local_pdf_path: str,
        authors: str
):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO publications 
                (title, summary, tags, year_published, organization, country, 
                    language, pdf_link, local_pdf_path, authors)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (title, summary, ", ".join(tags), year_published, organization, 
                    country, language, pdf_link, local_pdf_path, authors))
            conn.commit()
            return cursor.lastrowid
    
    def get_publications(self, page=1, per_page=20):
        offset = (page - 1) * per_page
        
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM publications')
            total = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT * FROM publications 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            ''', (per_page, offset))
            publications = cursor.fetchall()
            
            return publications, total
    
    def get_publication_by_id(self, pub_id):
        with self.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM publications WHERE id = ?', (pub_id,))
            return cursor.fetchone()




if __name__ == "__main__":
    test_db = Database("library.db")
    print([item for item in test_db.get_publications()[0][0]])