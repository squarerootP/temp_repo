from backend.src.domain.entities.chat_history import ChatMessage
from backend.src.infrastructure.persistence.models import ChatMessageModel


class ChatMessageMapper:
    """Handles conversion between ChatMessage entity and ChatMessageModel."""

    # -------------------------------------------------------------------------
    # Entity → Model
    # -------------------------------------------------------------------------
    @staticmethod
    def to_model(session_id: str, entity: ChatMessage) -> ChatMessageModel:
        """Convert ChatMessage entity to ChatMessageModel."""
        return ChatMessageModel(
            session_id=session_id,
            content=entity.content,
            role=entity.role,
            timestamp=entity.timestamp,
        )

    # -------------------------------------------------------------------------
    # Model → Entity
    # -------------------------------------------------------------------------
    @staticmethod
    def to_entity(model: ChatMessageModel) -> ChatMessage:
        """Convert ChatMessageModel to ChatMessage entity."""
        return ChatMessage(
            content=model.content,
            role=model.role,
            timestamp=model.timestamp,
        )
