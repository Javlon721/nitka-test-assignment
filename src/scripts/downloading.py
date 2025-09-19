from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
import pathlib
import arxiv
from src.config import Config
import shutil

class PDFDownloader:
    def __init__(self):
        self.pdfs_folder = Config.PDFS_FOLDER
        self.downloaded_papers = []
        self.create_pdfs_file()
    
    def clear_pdfs(self):
        shutil.rmtree(self.pdfs_folder)
        self.create_pdfs_file()


    def create_pdfs_file(self):
        os.makedirs(self.pdfs_folder, exist_ok=True)


    def download_from_arxiv(self, max_results=100, max_workers=8):
        """Download papers from ArXiv"""
        print(f"Downloading {max_results} papers from ArXiv...")
        papers = self._papers_to_download(max_results)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self._download_paper, paper) for paper in papers]

            for future in as_completed(futures):
                result = future.result()
                if result:
                    self.downloaded_papers.append(result)
        print(f"Successfully downloaded {len(self.downloaded_papers)} papers")
        return self.downloaded_papers


    def _download_paper(self, paper):
            try:
                safe_title = "".join(c for c in paper.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title[:50]
                filename = f"{paper.entry_id.split('/')[-1]}_{safe_title}.pdf"
                filepath = pathlib.Path(self.pdfs_folder, filename)

                print(f"Downloading: {paper.title[:60]}...")
                paper.download_pdf(self.pdfs_folder)

                return {
                    'title': paper.title,
                    'summary': paper.summary,
                    'authors': [str(author) for author in paper.authors],
                    'published': str(paper.published),
                    'pdf_url': paper.pdf_url,
                    'local_path': str(filepath),
                    'categories': paper.categories
                }
            except Exception as e:
                print(f"Error downloading {paper.title}: {e}")
                return None


    def _papers_to_download(self, max_results=100):
        categories = ['cs.AI', 'cs.ML', 'cs.CL', 'stat.ML', 'cs.CV']
        for category in categories:
            try:
                search = arxiv.Client().results(
                    search=arxiv.Search(
                        query=f'cat:{category}', 
                        max_results=max_results, 
                        sort_by=arxiv.SortCriterion.SubmittedDate
                    ),
                )
                return search
            except Exception as e:
                print(f"Error searching category {category}: {e}")



def main():
    downloader = PDFDownloader()
    downloader.clear_pdfs()
    arxiv_papers = downloader.download_from_arxiv(2)
    print(json.dumps(arxiv_papers, indent=4))
    print(f"\nTotal papers collected: {len(downloader.downloaded_papers)}")

if __name__ == "__main__":
    main()