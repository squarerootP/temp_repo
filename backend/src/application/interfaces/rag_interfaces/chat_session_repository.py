from abc import ABC, abstractmethod
from typing import List, Optional

from backend.src.domain.entities.rag_entities.chat_history import (ChatMessage,
                                                                   ChatSession)


class IChatSessionRepository(ABC):
    """Abstract repository for managing chat sessions."""

    @abstractmethod
    def create_session(self, chat_session: ChatSession) -> ChatSession:
        """Create and persist a new chat session."""
        pass

    @abstractmethod
    def get_session_by_id(self, session_id: str) -> Optional[ChatSession]:
        """Retrieve a chat session by its unique session ID."""
        pass

    @abstractmethod
    def get_sessions_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[ChatSession]:
        """Retrieve all chat sessions for a given user."""
        pass

    @abstractmethod # NOT YET USED
    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session and return True if successful."""
        pass
    
    @abstractmethod
    def add_message_to_session(self, session_id: str, message: ChatMessage) -> None:
        """Add a message to an existing chat session."""
        pass
