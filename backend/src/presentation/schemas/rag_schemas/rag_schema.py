import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class QuerySchema(BaseModel):
    """Schema for a user query."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    timestamp: datetime = Field(default_factory=datetime.now)
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    class Config:
        from_attributes = True
        from_attributes = True


class ResponseSchema(BaseModel):
    """Schema for a model-generated response to a query."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    answer: str
    source_chunks: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    query_id: str = ""
    confidence: Optional[float] = None
    session_id: Optional[str] = None

    class Config:
        from_attributes = True
        from_attributes = True
