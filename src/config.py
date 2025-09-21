from pathlib import Path
from pydantic_settings import BaseSettings

class _Config(BaseSettings):

    # AI
    GEMINI_API_KEY: str
    TEST_GENERATED_DATA_PATH: str
    GEMINI_MODEL: str

    BASEDIR: Path = Path.cwd()

    # Database
    DATABASE_PATH: str
    DATABASE_NAME: str

    # PDFS
    PDFS_FOLDER_PATH: str
    LOADED_PDFS_PATH: str

    # PDF-source managment
    ARXIV_BASE_URL: str
    PUBLICATIONS_PER_PAGE: int
    MAX_RESULTS: int

    END_VALUE_IN_CHANNELS: str


    @property
    def DATABASE_FILE_PATH(self) -> str:
      return self.create_relative_path(self.DATABASE_PATH)


    @property
    def DATABASE_LINK(self) -> str:
      return self.create_relative_path(self.DATABASE_PATH, self.DATABASE_NAME)


    @property
    def PDFS_FOLDER(self) -> str:
        return self.create_relative_path(self.PDFS_FOLDER_PATH)


    @property
    def LOADED_PDFS_URL(self) -> str:
        return self.create_relative_path(self.LOADED_PDFS_PATH)


    @property
    def TEST_GENERATED_DATA_URL(self) -> str:
          return self.create_relative_path(self.TEST_GENERATED_DATA_PATH)


    def create_relative_path(self, *paths: str) -> str:
      if not paths:
        raise ValueError("relative_path should take at least one path")

      return str(self.BASEDIR.joinpath(*paths))


Config = _Config(_env_file=".env")