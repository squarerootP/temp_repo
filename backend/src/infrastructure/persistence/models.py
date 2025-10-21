from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    TIMESTAMP,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from backend.src.domain.entities.chat_history import MessageRole


# --- Base ---
class Base(DeclarativeBase):
    """Base declarative class for all models."""
    pass


# --- User ---
class UserModel(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    second_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    address: Mapped[Optional[str]] = mapped_column(Text)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[Literal["member", "admin"]] = mapped_column(
        SQLEnum("member", "admin", name="user_roles"),
        nullable=False,
        default="member",
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )

    # Relationships
    borrowings: Mapped[List["BorrowingManagerModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    currently_borrowed_books: Mapped[List["BookModel"]] = relationship(
        back_populates="borrower", foreign_keys="BookModel.currently_borrowed_by"
    )

    def __repr__(self) -> str:
        return (
            f"<User(id={self.user_id}, email='{self.email}', "
            f"role='{self.role}', is_active={self.is_active})>"
        )


# --- Author ---
class AuthorModel(Base):
    __tablename__ = "authors"

    author_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    biography: Mapped[Optional[str]] = mapped_column(Text)

    books: Mapped[List["BookModel"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Author(id={self.author_id}, name='{self.first_name} {self.last_name}', "
            f"email='{self.email}')>"
        )


# --- Book ---
class BookModel(Base):
    __tablename__ = "books"

    book_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    book_isbn: Mapped[str] = mapped_column(String(13), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    genre: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    published_year: Mapped[Optional[int]] = mapped_column(Integer)
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.author_id"), nullable=False)
    currently_borrowed_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.user_id"), nullable=True
    )

    # Relationships
    author: Mapped["AuthorModel"] = relationship(back_populates="books")
    borrower: Mapped[Optional["UserModel"]] = relationship(
        back_populates="currently_borrowed_books",
        foreign_keys=[currently_borrowed_by],
    )
    borrowings: Mapped[List["BorrowingManagerModel"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Book(isbn='{self.book_isbn}', title='{self.title}', "
            f"author_id={self.author_id})>"
        )


# --- Borrowing Manager ---
class BorrowingManagerModel(Base):
    __tablename__ = "borrowings"

    borrow_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    book_isbn: Mapped[str] = mapped_column(ForeignKey("books.book_isbn"), nullable=False)
    borrow_date: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[Literal["borrowed", "returned", "overdue"]] = mapped_column(
        SQLEnum("borrowed", "returned", "overdue", name="borrow_status"),
        default="borrowed",
        index=True,
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(back_populates="borrowings")
    book: Mapped["BookModel"] = relationship(back_populates="borrowings")

    def __repr__(self) -> str:
        return (
            f"<Borrowing(id={self.borrow_id}, user_id={self.user_id}, "
            f"book_isbn='{self.book_isbn}', status='{self.status}')>"
        )


# --- Chat Session ---
class ChatSessionModel(Base):
    __tablename__ = "chat_sessions"

    session_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now, onupdate=datetime.now)
    metadata_json: Mapped[Optional[str]] = mapped_column("metadata", Text)

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
    role: Mapped[MessageRole] = mapped_column(nullable=False)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now)

    # Relationships
    session: Mapped["ChatSessionModel"] = relationship(back_populates="messages")

    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.message_id}, role='{self.role}', session='{self.session_id}')>"
