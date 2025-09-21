from pydantic import BaseModel, Field

class PublicationLocation(BaseModel):
    pdf_link: str = ""
    local_pdf_path: str = ""


class Publication(BaseModel):
    title: str = ""
    summary: str = ""
    tags: list[str] = Field(default_factory=list)
    year_published:str = ""
    organization: str = ""
    country: str = ""
    language: str = ""

class PublicationInfo(PublicationLocation, Publication):
    pass
