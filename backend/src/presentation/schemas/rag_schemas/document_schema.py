import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DocumentUploadResponse(BaseModel):
    """Response schema after uploading a document."""

    book_isbn: str
    title: str
    hash: str

    class Config:
        from_attributes = True