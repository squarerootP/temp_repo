from backend.src.domain.entities.chat_history import ChatSession
from backend.src.application.interfaces.chat_history_repository import \
    ChatHistoryRepository
    
def get_user_sessions(self, user_id: int, chat_repo:ChatHistoryRepository) -> list[ChatSession]:
    """Use case to retrieve all chat sessions for a specific user"""

    user_sessions = chat_repo.get_sessions_by_user(user_id=user_id)
    return user_sessions