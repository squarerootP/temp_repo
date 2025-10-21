import json
from typing import List
from backend.src.domain.entities.chat_history import ChatSession
from backend.src.infrastructure.persistence.models import ChatSessionModel
from backend.src.infrastructure.adapters.mappers.chat_message_mapper import ChatMessageMapper


class ChatSessionMapper:
    """Handles conversion between ChatSession entity and ChatSessionModel."""

    # -------------------------------------------------------------------------
    # Entity → Model
    # -------------------------------------------------------------------------
    @staticmethod
    def to_model(entity: ChatSession) -> ChatSessionModel:
        """Convert ChatSession entity to ChatSessionModel."""
        return ChatSessionModel(
            session_id=entity.session_id,
            user_id=entity.user_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            metadata_json=json.dumps(entity.metadata) if entity.metadata else None,
        )

    # -------------------------------------------------------------------------
    # Model → Entity
    # -------------------------------------------------------------------------
    @staticmethod
    def to_entity(model: ChatSessionModel, include_messages: bool = True) -> ChatSession:
        """Convert ChatSessionModel to ChatSession entity.
        Set `include_messages=False` to skip message mapping for performance.
        """
        metadata = json.loads(model.metadata_json) if model.metadata_json else {}

        messages = []
        if include_messages and getattr(model, "messages", None):
            messages = [
                ChatMessageMapper.to_entity(msg)
                for msg in model.messages
            ]

        return ChatSession(
            session_id=model.session_id,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            metadata=metadata,
            messages=messages,
        )
