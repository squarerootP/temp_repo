from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from backend.src.application.interfaces.chat_history_repository import ChatHistoryRepository
from backend.src.domain.entities.chat_history import ChatMessage, ChatSession
from backend.src.infrastructure.persistence.models import (
    ChatSessionModel,
)
from backend.src.infrastructure.adapters.mappers.chat_message_mapper import ChatMessageMapper
from backend.src.infrastructure.adapters.mappers.chat_session_mapper import ChatSessionMapper


class ChatHistoryRepositoryImpl(ChatHistoryRepository):
    """Implementation of ChatHistoryRepository using SQLAlchemy."""

    def __init__(self, db: Session):
        self.db = db

    # -------------------------------------------------------------------------
    # Session Methods
    # -------------------------------------------------------------------------
    def create_session(self, chat_session: ChatSession) -> ChatSession:
        """Create a new chat session and return it as a domain entity."""
        db_session = ChatSessionMapper.to_model(chat_session)

        try:
            self.db.add(db_session)
            self.db.commit()
            self.db.refresh(db_session)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to create chat session: {e}") from e

        return ChatSessionMapper.to_entity(db_session)

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Retrieve a single session by ID."""
        db_session = (
            self.db.query(ChatSessionModel)
            .filter(ChatSessionModel.session_id == session_id)
            .first()
        )
        return ChatSessionMapper.to_entity(db_session) if db_session else None

    def get_sessions_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[ChatSession]:
        """Retrieve multiple sessions for a given user, sorted by last update."""
        db_sessions = (
            self.db.query(ChatSessionModel)
            .filter(ChatSessionModel.user_id == user_id)
            .order_by(ChatSessionModel.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [ChatSessionMapper.to_entity(session, include_messages=False)
                for session in db_sessions]

    def delete_session(self, session_id: str) -> None:
        """Delete a chat session and all its messages."""
        try:
            deleted = (
                self.db.query(ChatSessionModel)
                .filter(ChatSessionModel.session_id == session_id)
                .delete()
            )
            self.db.commit()
            if not deleted:
                raise ValueError(f"No chat session found with ID {session_id}")
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to delete chat session: {e}") from e

    # -------------------------------------------------------------------------
    # Message Methods
    # -------------------------------------------------------------------------
    def add_message(self, session_id: str, message: ChatMessage) -> ChatMessage:
        """Add a message to an existing session."""
        db_session = (
            self.db.query(ChatSessionModel)
            .filter(ChatSessionModel.session_id == session_id)
            .first()
        )

        if not db_session:
            raise ValueError(f"Chat session with ID {session_id} does not exist")

        db_message = ChatMessageMapper.to_model(session_id, message)
        db_session.updated_at = datetime.now()

        try:
            self.db.add(db_message)
            self.db.commit()
            self.db.refresh(db_message)
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RuntimeError(f"Failed to add message: {e}") from e

        return ChatMessageMapper.to_entity(db_message)
