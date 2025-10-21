from backend.src.domain.entities.chat_history import ChatMessage, MessageRole
from backend.src.application.interfaces.chat_history_repository import \
    ChatHistoryRepository

def add_user_message(
    chat_repo: ChatHistoryRepository,
    session_id: str,
    content: str
) -> ChatMessage:
    """Use case to add a user message to a chat session"""

    user_message = ChatMessage(content=content, role=MessageRole.USER)
    added_message = chat_repo.add_message(session_id=session_id, message=user_message)
    return added_message

def add_assistant_message(
    chat_repo: ChatHistoryRepository,
    session_id: str,
    content: str
) -> ChatMessage:
    """Use case to add an assistant message to a chat session"""

    assistant_message = ChatMessage(content=content, role=MessageRole.ASSISTANT)
    added_message = chat_repo.add_message(session_id=session_id, message=assistant_message)
    return added_message