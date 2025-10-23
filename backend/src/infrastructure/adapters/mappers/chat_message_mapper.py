from backend.src.domain.entities._chat_history import ChatMessage
from backend.src.infrastructure.persistence.models._rag_models import ChatMessageModel


class ChatMessageMapper:
    """Handles conversion between ChatMessage entity and ChatMessageModel."""

    @staticmethod
    def to_model(session_id: str, entity: ChatMessage) -> ChatMessageModel:
        """Convert ChatMessage entity to ChatMessageModel."""
        return ChatMessageModel(
            session_id=session_id,
            content=entity.content,
            role=entity.role,
            timestamp=entity.timestamp,
        )

    @staticmethod
    def to_entity(model: ChatMessageModel) -> ChatMessage:
        """Convert ChatMessageModel to ChatMessage entity."""
        return ChatMessage(
            session_id=model.session_id,
            content=model.content,
            role=model.role,
            timestamp=model.timestamp,
        )
