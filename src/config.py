from dataclasses import dataclass
from pathlib import  Path


@dataclass
class _Config:

    # AI
    GEMINI_API_KEY: str = 'AIzaSyCCMm1VHhZR9gfNXyEpMgAKAHxjSYZu7xc'
    TEST_GENERATED_DATA_PATH: str = 'tmp/db/generated.json'
    GEMINI_MODEL: str = 'gemini-2.5-pro'

    BASEDIR: Path = Path.cwd()

    # Database
    DATABASE_PATH: str = 'tmp/db'
    DATABASE_NAME = 'library.db'

    # PDFS
    PDFS_FOLDER_PATH: str = 'tmp/pdfs'
    LOADED_PDFS_PATH: str = 'tmp/pdfs/data.json'

    # PDF-source managment
    ARXIV_BASE_URL: str = 'http://export.arxiv.org/api/query'
    PUBLICATIONS_PER_PAGE: int = 20
    MAX_RESULTS: int = 100

    END_VALUE_IN_CHANNELS: str = '!end!'


    @property
    def DATABASE_FILE_PATH(self) -> str:
      return self.BASEDIR.joinpath(self.DATABASE_PATH)


    @property
    def DATABASE_LINK(self) -> str:
      return self.BASEDIR.joinpath(self.DATABASE_PATH, self.DATABASE_NAME)


    @property
    def PDFS_FOLDER(self) -> str:
        return self.BASEDIR.joinpath(self.PDFS_FOLDER_PATH)


    @property
    def LOADED_PDFS_URL(self) -> str:
        return self.BASEDIR.joinpath(self.LOADED_PDFS_PATH)


    @property
    def TEST_GENERATED_DATA_URL(self) -> str:
          return self.create_relative_path(self.TEST_GENERATED_DATA_PATH)


    def create_relative_path(self, *paths: str):
      if not paths:
        raise ValueError("relative_path should take at least one path")

      return self.BASEDIR.joinpath(*paths)


Config = _Config()