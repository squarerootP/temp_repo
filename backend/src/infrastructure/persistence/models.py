from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from sqlalchemy import (TIMESTAMP, Boolean, DateTime, Enum, ForeignKey,
                        Integer, String, Text, func)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# --- Base ---
class Base(DeclarativeBase):
    pass


# --- User ---
class UserModel(Base):
    __tablename__ = "Users"

    user_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    second_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True)
    address: Mapped[Optional[str]] = mapped_column(Text)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    role: Mapped[Literal["member", "admin"]] = mapped_column(
        Enum("member", "admin", name="user_roles"), nullable=False, default="member"
    )
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp()
    )

    # relationships
    borrowings: Mapped[List["BorrowingManagerModel"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    currently_borrowed_books: Mapped[List["BookModel"]] = relationship(
        back_populates="borrower", foreign_keys="BookModel.currently_borrowed_by"
    )

    def __repr__(self) -> str:
        return f"<User(id={self.user_id}, email='{self.email}', role='{self.role}', is_active={self.is_active})>"


# --- Author ---
class AuthorModel(Base):
    __tablename__ = "Authors"

    author_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    biography: Mapped[Optional[str]] = mapped_column(Text)

    books: Mapped[List["BookModel"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Author(id={self.author_id}, email='{self.email}', name='{self.first_name} {self.last_name}')>"


# --- Book ---
class BookModel(Base):
    __tablename__ = "Books"

    book_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True, index=True)
    book_isbn: Mapped[str] = mapped_column(String(13), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    genre: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    published_year: Mapped[Optional[int]] = mapped_column(Integer)
    author_id: Mapped[int] = mapped_column(ForeignKey("Authors.author_id"), nullable=False)
    currently_borrowed_by: Mapped[Optional[int]] = mapped_column(
        ForeignKey("Users.user_id"), nullable=True
    )

    # relationships
    author: Mapped["AuthorModel"] = relationship(back_populates="books")
    borrower: Mapped[Optional["UserModel"]] = relationship(
        back_populates="currently_borrowed_books",
        foreign_keys=[currently_borrowed_by],
    )
    borrowings: Mapped[List["BorrowingManagerModel"]] = relationship(
        back_populates="book", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Book(book_isbn={self.book_isbn}, title='{self.title}', author_id={self.author_id})>"


# --- Borrowing Manager ---
class BorrowingManagerModel(Base):
    __tablename__ = "Borrowing"

    borrow_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("Users.user_id"), nullable=False)
    book_isbn: Mapped[str] = mapped_column(ForeignKey("Books.book_isbn"), nullable=False)
    borrow_date: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    status: Mapped[Literal["borrowed", "returned", "overdue"]] = mapped_column(
        Enum("borrowed", "returned", "overdue", name="status"),
        default="borrowed",
        index=True,
    )

    # relationships
    user: Mapped["UserModel"] = relationship(back_populates="borrowings")
    book: Mapped["BookModel"] = relationship(back_populates="borrowings")

    def __repr__(self) -> str:
        return (
            f"<BorrowingManager(id={self.borrow_id}, user_id={self.user_id}, "
            f"book_isbn='{self.book_isbn}', status='{self.status}')>"
        )
