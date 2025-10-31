from dataclasses import dataclass, field
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
    timestamp: datetime = field(default_factory=datetime.now)
    message_id: Optional[int] = None

    def __post_init__(self):
        if not self.content:
            raise ValueError("Content cannot be empty")


@dataclass
class ChatSession:
    """Chat session that groups related messages"""

    session_id: str
    messages: List[ChatMessage]
    user_id: int
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        if not self.session_id:
            raise ValueError("Session ID cannot be empty")
