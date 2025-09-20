import json
import os
import PyPDF2
from pydantic import BaseModel
from src.scripts.downloading import LoadedPDFData
from src.config import Config
import time
from google import genai


class PDFInfo(BaseModel):
    title: str
    summary: str
    tags: list[str]
    year_published:str
    organization: str
    country: str
    language: str

class MetadataExtractor:

    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)


    def extract_text_from_pdf(self, pdf_path):
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                max_pages = min(3, len(pdf_reader.pages))
                for page_num in range(max_pages):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
                
                return text[:4000]
        except Exception as e:
            print(f"Error extracting text from {pdf_path}: {e}")
            return ""


    def extract_metadata_with_ai(self, paper_info: LoadedPDFData):
        try:
            my_file = self.client.files.upload(file=paper_info.local_path)
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
            print("Request send")
            
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=[
                    promt,
                    my_file
                ],
                config={
                'response_mime_type': 'application/json',
                'response_schema': PDFInfo,
        },
            )
            
            return response.parsed.model_dump()
        except Exception as e:
            print(e)
            return None


    def process_papers(self, papers_data: list[LoadedPDFData]):
        print(f"Extracting {len(papers_data)} papers...")

        processed_papers = []
        
        for i, paper in enumerate(papers_data):
            print(f"Processing paper {i+1}/{len(papers_data)}: {paper.title[:50]}...")

            if os.path.exists(paper.local_path):
                metadata = self.extract_metadata_with_ai(paper)
                if not metadata:
                    continue

                processed_paper = {
                    **metadata,
                    'pdf_link': paper.pdf_url,
                    'local_pdf_path': paper.local_path,
                }
                
                processed_papers.append(processed_paper)
                
                time.sleep(1) # todo: delete on production
        
        return processed_papers


def main():
    extractor = MetadataExtractor()
    try:
        with open(Config.LOADED_PDFS_URL, 'r') as f:
            papers_data = [LoadedPDFData(**item) for item in json.load(f)]
    except FileNotFoundError:
        print(f"No {Config.LOADED_PDFS_URL} found")
        return

    processed_papers = extractor.process_papers(papers_data)
    
    with open(Config.TEST_GENERATED_DATA_URL, 'w') as f:
        json.dump(processed_papers, f, indent=2)

    print(f"Successfully processed {len(processed_papers)} papers")


if __name__ == "__main__":
    main()