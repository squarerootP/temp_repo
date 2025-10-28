from typing import List, Optional

from backend.src.application.interfaces.rag_interfaces.chat_session_repository import \
    IChatSessionRepository
from backend.src.domain.entities.rag_entities.chat_history import (ChatMessage,
                                                                   ChatSession)


def create_chat_session(
    chat_repo: IChatSessionRepository,
    user_id: Optional[int] = None,
    initial_messages: Optional[List[ChatMessage]] = None
) -> ChatSession:
    """Create a new chat session with optional initial messages"""
    if initial_messages is None:
        initial_messages = []
    
    new_session = ChatSession(
        session_id="",  # ID will be set by the repository
        messages=initial_messages,
        user_id=user_id
    )
    
    created_session = chat_repo.create_session(new_session)
    
    return created_session

    