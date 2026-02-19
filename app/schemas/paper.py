from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

class PaperBase(BaseModel):
    title: str
    abstract: Optional[str] = None
    journal: str
    publication_date: Optional[date] = None
    full_text_link: Optional[str] = None
    doi: Optional[str] = None
    pubmed_id: str
    authors: Optional[List[str]] = []

class PaperResponse(PaperBase):
    id: str
    created_at: datetime

    class Config:
        from_attributes = True

class PapersListResponse(BaseModel):
    papers: List[PaperResponse]
    total: int
    page: int
    size: int
