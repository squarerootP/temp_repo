import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessageRequest(BaseModel):
    """Request schema for sending a chat message."""
    content: str = Field(..., min_length=1, description="Message content")
    session_id: str 
    user_id: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "1",
                "content": "What is this document about?"
            }
        }


class  ChatMessageResponse(BaseModel):
    """Response schema for individual messages."""
    content: str
    role: MessageRole
    timestamp: datetime

    class Config:
        from_attributes = True


class ChatSessionRequest(BaseModel):
    """Request to start or continue a chat session."""
    session_id: Optional[str] = None  # None = create new session
    message: str = Field(..., min_length=1)
    user_id: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "abc-123",
                "message": "Tell me about the uploaded documents"
            }
        }


class ChatSessionResponse(BaseModel):
    """Response with session info and messages."""
    session_id: str
    user_id: Optional[int] = None
    messages: List[ChatMessageResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """Simple response for a single chat interaction."""
    session_id: str
    user_message: str
    assistant_response: str
    timestamp: datetime = Field(default_factory=datetime.now)