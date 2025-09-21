import asyncio
import os

from google import genai

from src.scripts.utils import print_shifts
from src.scripts.db.connection import Publication, PublicationInfo
from src.scripts.downloading import LoadedPDFData
from src.config import Config



class MetadataExtractor:

    def __init__(self, loaded_ch: asyncio.Queue[LoadedPDFData], extracted_ch: asyncio.Queue[PublicationInfo]):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.loaded_ch = loaded_ch
        self.extracted_ch = extracted_ch

    async def extract_metadata_with_ai(self, paper_info: LoadedPDFData):
        try:

            my_file = await self.client.aio.files.upload(file=paper_info.local_pdf_path)
            promt = f"""
                Extract and analyze the following academic paper information and return a JSON object with the specified fields.
                
                Return a JSON object with these exact fields:
                {{
                    "title": "cleaned and formatted title",
                    "summary": "concise summary (max 500 words)",
                    "tags": "comma-separated relevant tags/keywords",
                    "year_published": year as integer,
                    "organization": "primary research institution/university",
                    "country": "country of primary institution", 
                    "language": "language of the paper"
                }}
                
                Rules:
                - Extract year from published date
                - Generate 5-10 relevant tags based on content
                - Identify the primary research organization from authors' affiliations
                - Determine the country based on the organization
                - Default language to "English" unless clearly stated otherwise
                - If information is not available, use reasonable defaults or "Unknown"
            
                IMPORTANT: Return ONLY the JSON object, no additional text or formatting.
            """
            
            response = await self.client.aio.models.generate_content(
                model=Config.GEMINI_MODEL,
                contents=[
                    promt,
                    my_file
                ],
                config={
                'response_mime_type': 'application/json',
                'response_schema': Publication,
        },
            )
            
            self.extracted_ch.put_nowait(
                PublicationInfo(
                    **response.parsed.model_dump(),
                    pdf_link=paper_info.pdf_link,
                    local_pdf_path=paper_info.local_pdf_path
                    )
                )
        except Exception as e:
            print(e)
            return None


    async def handle_paper(self, paper):
        paper_title= paper.title[:50]

        print_shifts(f"Start processing paper {paper_title}...")

        if os.path.exists(paper.local_pdf_path):
            await self.extract_metadata_with_ai(paper)
            print_shifts(f"End processing paper {paper_title}")


    async def process_papers(self):
        print_shifts("Extracting papers...")

        async with asyncio.TaskGroup() as tg:
            while True:
                paper = await self.loaded_ch.get()
                if paper == Config.END_VALUE_IN_CHANNELS:
                    break
                try:
                    tg.create_task(self.handle_paper(paper))
                except Exception as e:
                    print(e)

        await self.extracted_ch.put(Config.END_VALUE_IN_CHANNELS)
