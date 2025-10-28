from backend.src.application.interfaces.rag_interfaces.chat_session_repository import \
    IChatSessionRepository
from backend.src.domain.entities.rag_entities.chat_history import ChatSession
from backend.src.domain.exceptions.chat_exceptions import ChatHistoryNotFound


def get_session_history(session_id: str, chat_repo:IChatSessionRepository) -> ChatSession | None:
    """Use case to retrieve the chat session history by session ID"""
    
    chat_session = chat_repo.get_session_by_id(session_id=session_id)
    if not chat_session:
        raise ChatHistoryNotFound(f"Chat session with ID {session_id} not found.")
    return chat_session