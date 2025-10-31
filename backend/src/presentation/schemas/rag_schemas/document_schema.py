import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class DocumentChunkSchema(BaseModel):
    """Schema for a document chunk (mirrors LangChain's Document)."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    page_content: str
    document_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        from_attributes = True
        from_attributes = True


class DocumentSchema(BaseModel):
    """Schema for a full document with its metadata and chunks."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    hash: Optional[str] = None
    chunks: List[DocumentChunkSchema] = Field(default_factory=list)
    uploaded_at: datetime = Field(default_factory=datetime.now)
    user_id: Optional[int] = None

    class Config:
        from_attributes = True
        from_attributes = True


class DocumentUploadResponse(BaseModel):
    """Response schema after uploading a document."""

    document_id: str
    title: str
    hash: str
    chunk_count: int
    uploaded_at: datetime

    class Config:
        from_attributes = True
        from_attributes = True
