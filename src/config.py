from dataclasses import dataclass
import os
from pathlib import  Path


@dataclass
class _Config:
    OPENAI_API_KEY: str = os.getenv('OPENAI_API_KEY')
    
    BASEDIR: Path = Path.cwd()
    database_path: str = 'tmp/db/library.db'
    pdfs_folder: str = 'tmp/pdfs'
    
    ARXIV_BASE_URL: str = 'http://export.arxiv.org/api/query'
    
    PUBLICATIONS_PER_PAGE: int = 20
    MAX_RESULTS: int = 100
    
    @property
    def DATABASE_PATH(self) -> str:
      return self.BASEDIR.joinpath(self.database_path)


    @property
    def PDFS_FOLDER(self) -> str:
        return self.BASEDIR.joinpath(self.pdfs_folder)


Config = _Config()