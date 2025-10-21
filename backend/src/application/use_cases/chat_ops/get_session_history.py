from backend.src.domain.entities.chat_history import ChatSession
from backend.src.application.interfaces.chat_history_repository import \
    ChatHistoryRepository
from backend.src.domain.exceptions.chat_exceptions import ChatHistoryNotFound    

def get_session_history(self, session_id: str, chat_repo:ChatHistoryRepository) -> ChatSession | None:
    """Use case to retrieve the chat session history by session ID"""
    
    chat_session = chat_repo.get_session(session_id=session_id)
    if not chat_session:
        raise ChatHistoryNotFound(f"Chat session with ID {session_id} not found.")
    return chat_session