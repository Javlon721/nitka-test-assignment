import asyncio

from src.scripts.db.connection import Database, Publication
from src.scripts.extracting import MetadataExtractor
from src.config import Config
from src.scripts.downloading import PDFDownloader


async def main():
  loaded_ch = asyncio.Queue()
  extracted_ch = asyncio.Queue()
  # MAX_PAPERS = Config.MAX_RESULTS
  MAX_PAPERS = 2

  downloader = PDFDownloader(loaded_ch)
  papers = downloader.download_from_arxiv(MAX_PAPERS)

  extractor = MetadataExtractor(loaded_ch, extracted_ch)
  processed_papers = extractor.process_papers()

  db = Database(extracted_ch)
  
  db.clear_db_folder()
  db.init_db()
  
  await asyncio.gather(papers, processed_papers, db.consumer())
  
if __name__ == "__main__":
    asyncio.run(main())