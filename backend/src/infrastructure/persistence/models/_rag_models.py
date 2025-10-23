from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional

from sqlalchemy import TIMESTAMP, Boolean, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from backend.src.domain.entities._chat_history import MessageRole
from backend.src.infrastructure.persistence.models.normal_models import Base

# --- Chat Session ---
class ChatSessionModel(Base):
    __tablename__ = "chat_sessions"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    created_at: Mapped[datetime] = mapped_column(default_factory=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default_factory=datetime.now, onupdate=datetime.now)
    # Relationships
    messages: Mapped[List["ChatMessageModel"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<ChatSession(id={self.session_id}, user_id={self.user_id})>"


# --- Chat Message ---
class ChatMessageModel(Base):
    __tablename__ = "chat_messages"

    message_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    session_id: Mapped[str] = mapped_column(
        ForeignKey("chat_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole), nullable=False) #type: ignore
    timestamp: Mapped[datetime] = mapped_column(default_factory=datetime.now) 

    # Relationships
    session: Mapped["ChatSessionModel"] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.message_id}, role='{self.role.name}', session='{self.session_id}')>"