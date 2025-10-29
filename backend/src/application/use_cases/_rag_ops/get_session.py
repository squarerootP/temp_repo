from backend.src.application.interfaces.rag_interfaces.chat_session_repository import \
    IChatSessionRepository
from backend.src.domain.entities.library_entities import User
from backend.src.domain.entities.rag_entities.chat_history import ChatSession
from backend.src.domain.exceptions.chat_exceptions import (
    ChatHistoryNotFound, NotAuthorizedToViewSession)


def get_session_history(user: User, session_id: str, chat_repo:IChatSessionRepository) -> ChatSession:
    """Use case to retrieve the chat session history by session ID"""
    if user.role != "admin":
        user_sessions = chat_repo.get_sessions_by_user(user_id=user.user_id)
        if session_id not in user_sessions:
            raise NotAuthorizedToViewSession("You are not authorized to reach this history")
        
    chat_session = chat_repo.get_session_by_id(session_id=session_id)
    if not chat_session:
        raise ChatHistoryNotFound(f"Chat session with ID {session_id} not found.")
    return chat_session