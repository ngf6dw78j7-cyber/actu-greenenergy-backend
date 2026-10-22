from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class ArticleOut(BaseModel):
    id: UUID
    title: str
    original_url: str
    summary: Optional[str] = None
    image_url: Optional[str] = None
    category: Optional[str] = None
    region: Optional[str] = None
    source: Optional[str] = None
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True
