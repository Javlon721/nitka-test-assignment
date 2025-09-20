import json
from src.scripts.connection import Database, Publication
from src.scripts.extracting import MetadataExtractor
from src.config import Config
from src.scripts.downloading import PDFDownloader



def print_shifts(count: int = 100, shifter: str = '-'):
    print(shifter * count)


def main():

  MAX_PAPERS = 2 #todo: remake to Config.MAX_RESULTS

  downloader = PDFDownloader()
  papers = downloader.download_from_arxiv(MAX_PAPERS)

  print_shifts()

  extractor = MetadataExtractor()
  processed_papers = extractor.process_papers(papers)

  print_shifts()

  db = Database()

  #todo: delete this to guys
  db.clear_db_folder()
  db.init_db()
  
  db.insert_publications([Publication(**item) for item in processed_papers])
  print(json.dumps(db.get_publications(), indent=4))
  
if __name__ == "__main__":
    main()