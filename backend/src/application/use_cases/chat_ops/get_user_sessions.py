from backend.src.application.interfaces.rag_interfaces.chat_session_repository import \
    IChatSessionRepository
from backend.src.domain.entities.rag_entities.chat_history import ChatSession


def get_user_sessions(user_id: int, chat_repo:IChatSessionRepository) -> list[ChatSession]:
    """Use case to retrieve all chat sessions for a specific user"""

    user_sessions = chat_repo.get_sessions_by_user(user_id=user_id)
    return user_sessions