from sqlalchemy import (TIMESTAMP, Boolean, Column, DateTime, Enum, ForeignKey,
                        Integer, String, Text, func)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class BorrowingManager(Base):
    __tablename__ = "Borrowing"

    borrow_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("Users.user_id"), nullable=False)
    book_isbn = Column(String, ForeignKey("Books.isbn"), nullable=False)
    borrow_date = Column(DateTime, default=func.now())
    due_date = Column(DateTime)
    status = Column(Enum("borrowed", "returned", "overdue"), name="status", 
                    default="borrowed", index=True)

    user = relationship("User", back_populates="borrowings")
    book = relationship("Book", back_populates="borrowings")
    def __repr__(self):
        return f"<BorrowingManager(id={self.borrow_id}, user_id={self.user_id}, \
            book_isbn='{self.book_isbn}', status='{self.status}')>"
    
class User(Base):
    __tablename__ = "Users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    second_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), unique=True)
    address = Column(Text)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(Enum('member', 'admin', name='user_roles'), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())

    borrowings = relationship('BorrowingManager', back_populates="user", cascade="all, delete-orphan")
    currently_borrowed_books = relationship("Book", back_populates="borrower",
                                            foreign_keys="Book.currently_borrowed_by")
    def __repr__(self):
        return f"<User(id={self.user_id}, \
            email='{self.email}', role='{self.role}', is_active={self.is_active})>"
class Book(Base):
    __tablename__ = "Books"

    book_id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    isbn = Column(String(13), unique=True, index=True)
    title = Column(String(200), nullable=False)
    summary = Column(Text)
    genre = Column(String(50), index=True)
    published_year = Column(Integer)
    author_id = Column(Integer, ForeignKey("Authors.author_id"), nullable=False)
    currently_borrowed_by = Column(Integer, ForeignKey("Users.user_id"), nullable=True)



    author = relationship("Author", back_populates="books")
    borrower = relationship("User", back_populates="currently_borrowed_books", 
                            foreign_keys=[currently_borrowed_by])
    borrowings = relationship("BorrowingManager", back_populates="book", cascade="all, delete-orphan")
    def __repr__(self):
        return f"<Book(isbn={self.isbn}, title='{self.title}', author_id={self.author_id})>"   


class Author(Base):
    __tablename__ = "Authors"

    author_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    biography = Column(Text)

    books = relationship("Book", back_populates="author", cascade="all, delete-orphan")
    def __repr__(self):
        return f"<Author(id={self.author_id}, email='{self.email}', name='{self.first_name} {self.last_name}')>"

 
