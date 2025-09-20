import asyncio
import json
from src.scripts.connection import Database, Publication
from src.scripts.extracting import MetadataExtractor
from src.config import Config
from src.scripts.downloading import PDFDownloader



def print_shifts(msg: str):
    print(msg)
    print()


async def test_extract_consumer(ch: asyncio.Queue):
    print_shifts('test_extract_consumer starts...')
    while True:
        data = await ch.get()

        if data == Config.END_VALUE_IN_CHANNELS:
            return

        print(data)


async def main():
  loaded_ch = asyncio.Queue()
  extracted_ch = asyncio.Queue()
  MAX_PAPERS = 2 #todo: remake to Config.MAX_RESULTS

  downloader = PDFDownloader(loaded_ch)
  papers = downloader.download_from_arxiv(MAX_PAPERS)

  extractor = MetadataExtractor(loaded_ch, extracted_ch)
  processed_papers = extractor.process_papers()

  await asyncio.gather(papers, processed_papers, test_extract_consumer(extracted_ch))
  
if __name__ == "__main__":
    asyncio.run(main())