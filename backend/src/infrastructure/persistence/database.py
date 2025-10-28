from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.src.infrastructure.config.settings import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL, 
                       connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, 
                            autocommit=False, autoflush=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables in the database."""
    # Import Base from normal_models (the actual declarative base used by all models)
    from backend.src.infrastructure.persistence.models.normal_models import (
        AuthorModel, Base, BookModel, BorrowingManagerModel, UserModel)
    from backend.src.infrastructure.persistence.models.rag_models import (
        ChatMessageModel, ChatSessionModel, DocumentModel)

    # Create all tables in the main database
    Base.metadata.create_all(bind=engine)
    print("✅ All tables created successfully!")