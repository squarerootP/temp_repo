from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional

from sqlalchemy import TIMESTAMP, Boolean, DateTime
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from backend.src.domain.entities.rag_entities.chat_history import MessageRole


# --- Base ---
class Base(DeclarativeBase):
    """Base declarative class for all models."""

    pass


# --- User ---
class UserModel(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    second_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[Literal["member", "admin"]] = mapped_column(
        SQLEnum("member", "admin", name="user_roles"),
        nullable=False,
        default="member",
    )


# --- Book ---
class BookModel(Base):
    __tablename__ = "books"

    book_isbn: Mapped[str] = mapped_column(String(13), primary_key=True, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    genre: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    published_year: Mapped[Optional[int]] = mapped_column(Integer)
    author_name: Mapped[str] = mapped_column(String(50))
    img_path: Mapped[Optional[str]] = mapped_column(String(255))
    # 1-to-1 relationship with Document
    document: Mapped[Optional["DocumentModel"]] = relationship( #type: ignore
        back_populates="book",
        uselist=False,
        cascade="all, delete-orphan",
    )
