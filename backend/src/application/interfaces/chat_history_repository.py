from abc import ABC, abstractmethod
from typing import List

from backend.src.domain.entities.chat_history import ChatSession, ChatMessage

class ChatHistoryRepository(ABC):
    """Interface for chat history repository"""
    
    @abstractmethod
    def create_session(self, chat_session: ChatSession)-> ChatSession:
        """Create a new chat session"""
        pass
    
    @abstractmethod
    def add_message(self, session_id: str, message: ChatMessage) -> ChatMessage:
        """Add a message to an existing chat session"""
        pass
    
    @abstractmethod
    def get_session(self, session_id: str) -> ChatSession | None:
        """Retrieve a chat session by its ID"""
        pass
    
    @abstractmethod
    def get_sessions_by_user(self, user_id: int) -> List[ChatSession]:
        """Retrieve all chat sessions for a specific user"""
        pass

    @abstractmethod
    def delete_session(self, session_id: str) -> None:
        """Delete a chat session by its ID"""
        pass