from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    
@dataclass
class ChatMessage:
    """Individual message in a chat session"""
    
    content: str
    role: MessageRole
    session_id: str
    timestamp: datetime = datetime.now()
    message_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.content:
            raise ValueError("Content cannot be empty")

@dataclass
class ChatSession:
    """Chat session that groups related messages"""
    session_id: str
    messages: List[ChatMessage]
    user_id: Optional[int]
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    
    def __post_init__(self):
        if not self.session_id:
            raise ValueError("Session ID cannot be empty")
        if not self.created_at:
            self.created_at = datetime.now()
        if not self.updated_at:
            self.updated_at = self.created_at
            
    def add_message(self, message: ChatMessage):
        """Add a message to the chat session and update timestamp"""
        self.messages.append(message)
        self.updated_at = datetime.now()
        
    def trim_messages(self, n: int) -> List[ChatMessage]:
        return self.messages[-n:]