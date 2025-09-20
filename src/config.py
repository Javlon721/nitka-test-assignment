from dataclasses import dataclass
import os
from pathlib import  Path


@dataclass
class _Config:
    # AI
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY')

    BASEDIR: Path = Path.cwd()

    # Database
    DATABASE_PATH: str = 'tmp/db'
    DATABASE_NAME = 'library.db'

    # PDFS
    PDFS_FOLDER_PATH: str = 'tmp/pdfs'

    # PDF-source managment
    ARXIV_BASE_URL: str = 'http://export.arxiv.org/api/query'
    PUBLICATIONS_PER_PAGE: int = 20
    MAX_RESULTS: int = 100
    
    @property
    def DATABASE_FILE_PATH(self) -> str:
      return self.BASEDIR.joinpath(self.DATABASE_PATH)


    @property
    def DATABASE_LINK(self) -> str:
      return self.BASEDIR.joinpath(self.DATABASE_PATH, self.DATABASE_NAME)


    @property
    def PDFS_FOLDER(self) -> str:
        return self.BASEDIR.joinpath(self.PDFS_FOLDER_PATH)


Config = _Config()