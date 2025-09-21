import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import Config
from src.scripts.connection import Database


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


test_ch = asyncio.Queue()
test_db = Database(test_ch)


@app.get('/')
async def get_publications(offset: int, limit: int= Config.PUBLICATIONS_PER_PAGE):
  return test_db.get_publications(offset, limit)


@app.get('/settings')
def get_settings():
  # i am lazy, so instead of using node_modules i am sending it via this silly endpoint :)
  return {
    "page_size": Config.PUBLICATIONS_PER_PAGE
  }