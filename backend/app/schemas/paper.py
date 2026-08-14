from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class PaperMetadata(BaseModel):
    paper_id: str
    filename: str
    title: Optional[str] = None
    num_pages: int
    uploaded_at: datetime
    char_count: int
    file_hash: str

class Chunk(BaseModel):
    chunk_id: str
    paper_id: str
    text: str
    chunk_index: int