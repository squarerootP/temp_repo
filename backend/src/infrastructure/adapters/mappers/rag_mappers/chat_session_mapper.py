import json
from typing import List

from backend.src.domain.entities.rag_entities.chat_history import (ChatMessage,
                                                                   ChatSession)
from backend.src.infrastructure.adapters.mappers.rag_mappers.chat_message_mapper import \
    ChatMessageMapper
from backend.src.infrastructure.persistence.models.rag_models import \
    ChatSessionModel


class ChatSessionMapper:
    """Handles conversion between ChatSession entity and ChatSessionModel."""

    @staticmethod
    def to_model(entity: ChatSession) -> ChatSessionModel:
        """Convert ChatSession entity to ChatSessionModel."""
        return ChatSessionModel(
            session_id=entity.session_id,
            user_id=entity.user_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def to_entity(
        model: ChatSessionModel, include_messages: bool = True
    ) -> ChatSession:
        """Convert ChatSessionModel to ChatSession entity.
        Set `include_messages=False` to skip message mapping for performance.
        """
        messages = []
        if include_messages and getattr(model, "messages", None):
            messages = [ChatMessageMapper.to_entity(msg) for msg in model.messages]

        return ChatSession(
            session_id=model.session_id,
            user_id=model.user_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
            messages=messages,
        )

    @staticmethod
    def serialize_messages(messages: List[ChatMessage]) -> List[dict]:
        return [{"role": msg.role.value, "content": msg.content} for msg in messages]
