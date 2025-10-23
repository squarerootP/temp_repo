
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from backend.src.infrastructure.config.settings import settings
from backend.src.infrastructure.adapters.rag.rag_config import rag_settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL, 
                       connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, 
                            autocommit=False, autoflush=False)
Base = declarative_base()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def get_rag_db(): 
    rag_db_engine = create_engine(rag_settings.CHROMA_PERSIST_DIR,
                                  connect_args={"check_same_thread": False}) 
    RAGSessionLocal = sessionmaker(bind=rag_db_engine, 
                                  autocommit=False, autoflush=False) 
    rag_db = RAGSessionLocal() 
    try: 
        yield rag_db 
    finally: 
        rag_db.close()
    