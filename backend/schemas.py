from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ChunkBase(BaseModel):
    chunk_index: int
    content: str

class Chunk(ChunkBase):
    id: str
    document_id: str

    class Config:
        from_attributes = True

class DocumentBase(BaseModel):
    url: str

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: str
    path: str
    section: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    title: Optional[str] = None
    source: str
    content: Optional[str] = None
    created_at: datetime
    chunks: List[Chunk] = []

    class Config:
        from_attributes = True

class ScrapeRequest(BaseModel):
    url: str
