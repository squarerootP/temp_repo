import json
from datetime import datetime
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.src.application.interfaces.rag_interfaces.chat_session_repository import \
    IChatSessionRepository
from backend.src.domain.entities.rag_entities.chat_history import (ChatMessage,
                                                                   ChatSession)
from backend.src.domain.exceptions.chat_exceptions import \
    ChatSessionNotFoundError
from backend.src.infrastructure.adapters.mappers.rag_mappers.chat_message_mapper import \
    ChatMessageMapper
from backend.src.infrastructure.adapters.mappers.rag_mappers.chat_session_mapper import \
    ChatSessionMapper
from backend.src.infrastructure.persistence.models.rag_models import \
    ChatSessionModel


class ChatSessionRepositoryImpl(IChatSessionRepository):
    """SQLAlchemy implementation of the ChatSession repository."""

    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------
    def create_session(self, chat_session: ChatSession) -> ChatSession:
        """Create a new chat session and return the persisted entity."""
        db_session = ChatSessionMapper.to_model(chat_session)

        try:
            self.db.add(db_session)
            self.db.commit()
            self.db.refresh(db_session)
            return ChatSessionMapper.to_entity(db_session)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to create chat session: {e}") from e

    # ------------------------------------------------------------
    # READ
    # ------------------------------------------------------------
    def get_session_by_id(self, session_id: str) -> Optional[ChatSession]:
        """Retrieve a chat session by its ID."""
        db_session = (
            self.db.query(ChatSessionModel)
            .filter(ChatSessionModel.session_id == session_id)
            .first()
        )
        return ChatSessionMapper.to_entity(db_session) if db_session else None

    def get_sessions_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[ChatSession]:
        """Retrieve chat sessions for a user, sorted by last update time."""
        db_sessions = (
            self.db.query(ChatSessionModel)
            .filter(ChatSessionModel.user_id == user_id)
            .order_by(ChatSessionModel.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return [
            ChatSessionMapper.to_entity(session, include_messages=False)
            for session in db_sessions
        ]

    # ------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------
    def update_session(self, session: ChatSession) -> None:
        """
        Update an existing chat session (messages, timestamps, metadata).
        Ensures both session info and related messages are correctly persisted.
        """
        try:
            orm_session = (
                self.db.query(ChatSessionModel)
                .filter_by(session_id=session.session_id)
                .first()
            )

            if not orm_session:
                raise ChatSessionNotFoundError

            # --- Update metadata and timestamp ---
            orm_session.updated_at = session.updated_at or datetime.now()

            # --- Replace messages if provided ---
            if session.messages:
                orm_session.messages.clear()
                for msg in session.messages:
                    orm_session.messages.append(
                        ChatMessageMapper.to_model(
                            session_id=session.session_id,
                            entity=msg
                        )
                    )

            self.db.commit()
            self.db.refresh(orm_session)

        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Database error while updating session: {e}") from e

    # ------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------
    def delete_session(self, session_id: str) -> bool:
        """Delete a chat session and all its messages."""
        try:
            deleted_count = (
                self.db.query(ChatSessionModel)
                .filter(ChatSessionModel.session_id == session_id)
                .delete()
            )
            self.db.commit()
            return deleted_count > 0

        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to delete chat session: {e}") from e

    # ------------------------------------------------------------
    # ADD MESSAGE
    # ------------------------------------------------------------
    def add_message_to_session(self, session_id: str, message: ChatMessage) -> None:
        """Append a message to an existing chat session."""
        db_session = (
            self.db.query(ChatSessionModel)
            .filter(ChatSessionModel.session_id == session_id)
            .first()
        )

        if not db_session:
            raise ChatSessionNotFoundError

        chatmessage_model = ChatMessageMapper.to_model(
            session_id=db_session.session_id,
            entity=message
        )

        db_session.messages.append(chatmessage_model)

        try:
            self.db.add(db_session)  # safe even if already attached
            self.db.commit()
            self.db.refresh(db_session)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to add message to session: {e}") from e
    def clear_session_messages(self, session_id: str) -> None:
        return super().clear_session_messages(session_id)
    