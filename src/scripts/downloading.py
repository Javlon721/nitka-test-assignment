import asyncio
import os
import pathlib
import shutil

import arxiv

from src.scripts.utils import print_shifts
from src.scripts.connection import PublicationLocation
from src.config import Config

class LoadedPDFData(PublicationLocation):
    title: str = ""


class PDFDownloader:

    def __init__(self, loaded_ch: asyncio.Queue):
        self.pdfs_folder = Config.PDFS_FOLDER
        self.create_pdfs_file()
        self.loaded_ch = loaded_ch


    def clear_pdfs(self):
        shutil.rmtree(self.pdfs_folder)
        self.create_pdfs_file()


    def create_pdfs_file(self):
        os.makedirs(self.pdfs_folder, exist_ok=True)


    async def download_from_arxiv(self, max_results=100, max_workers=8) -> list[LoadedPDFData]:
        print_shifts(f"Downloading {max_results} papers from ArXiv...")

        papers = self._papers_to_download(max_results)
        
        semaphore = asyncio.Semaphore(max_workers)
        async def run_download(paper):
            async with semaphore:
                return await asyncio.to_thread(self._download_paper, paper)

        tasks = [run_download(paper) for paper in papers]
        await asyncio.gather(*tasks, return_exceptions=True)
        await self.loaded_ch.put(Config.END_VALUE_IN_CHANNELS)

        print_shifts(f"Successfully downloaded {999} papers")


    def _download_paper(self, paper: arxiv.Result) -> LoadedPDFData:
            try:
                safe_title = "".join(c for c in paper.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title[:50]
                filename = f"{paper.entry_id.split('/')[-1]}_{safe_title}.pdf"
                filepath = pathlib.Path(self.pdfs_folder, filename)

                print_title = paper.title[:60]
                print_shifts(f"Start downloading: {print_title}...")

                paper.download_pdf(self.pdfs_folder, filename)

                print_shifts(f"End downloading: {print_title}...")

                self.loaded_ch.put_nowait(LoadedPDFData(
                        title= paper.title,
                        pdf_link= paper.pdf_url,
                        local_pdf_path= str(filepath)
                    ))
            except Exception as e:
                print(f"Error downloading {paper.title}: {e}")


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


async def test_consumer(ch: asyncio.Queue):
    while True:
        data: LoadedPDFData = await ch.get()

        if data == Config.END_VALUE_IN_CHANNELS:
            return

        print(data.title)


async def main():
    test_queue = asyncio.Queue()
    downloader = PDFDownloader(test_queue)
    downloader.clear_pdfs()
    await asyncio.gather(downloader.download_from_arxiv(2), test_consumer(test_queue))


if __name__ == "__main__":
    asyncio.run(main())