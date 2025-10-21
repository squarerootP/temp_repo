from typing import List, Optional

from backend.src.application.interfaces.chat_history_repository import \
    ChatHistoryRepository
from backend.src.domain.entities.chat_history import ChatSession, ChatMessage

def create_chat_session(
    chat_repo: ChatHistoryRepository,
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

    