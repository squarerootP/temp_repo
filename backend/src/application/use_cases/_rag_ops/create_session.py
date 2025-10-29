from typing import List, Optional

from backend.src.application.interfaces.rag_interfaces.chat_session_repository import \
    IChatSessionRepository
from backend.src.domain.entities.rag_entities.chat_history import (ChatMessage,
                                                                   ChatSession)


def create_chat_session(
    chat_repo: IChatSessionRepository,
    user_id: Optional[int] = None,
) -> ChatSession:
    """Create a new chat session with optional initial messages"""

    new_session = ChatSession(
        session_id="", 
        messages=[],
        user_id=user_id
    )
    
    created_session = chat_repo.create_session(new_session)
    
    return created_session

    