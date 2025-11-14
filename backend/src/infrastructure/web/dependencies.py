from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session

from backend.src.infrastructure.persistence.database import get_db
from backend.src.infrastructure.persistence.repository_impl.library_repos_impl.book_repository_impl import BookRepositoryImpl
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.chat_session_repository_impl import \
    ChatSessionRepositoryImpl
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.rag_repository_impl import \
    LangGraphRAGRepositoryImpl
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.vectorstore_repository_impl import \
    ChromaVectorStoreRepositoryImpl
from backend.src.infrastructure.persistence.repository_impl.rag_repos_impl.document_repository_impl import \
    DocumentRepositoryImpl

@lru_cache()
def get_vector_repo(db: Session = Depends(get_db)) -> ChromaVectorStoreRepositoryImpl:
    """Singleton instance of the Chroma vectorstore."""
    return ChromaVectorStoreRepositoryImpl(doc_repo=DocumentRepositoryImpl(db), book_repo=BookRepositoryImpl(db))


def get_chat_session_repo(db: Session = Depends(get_db)) -> ChatSessionRepositoryImpl:
    """Provides chat session repository per request."""
    return ChatSessionRepositoryImpl(db)
def get_book_repo(db: Session = Depends(get_db)) -> BookRepositoryImpl:
    return BookRepositoryImpl(db)
def get_rag_repo(
    vector_repo: ChromaVectorStoreRepositoryImpl = Depends(get_vector_repo),
    chat_repo: ChatSessionRepositoryImpl = Depends(get_chat_session_repo),
    book_repo: BookRepositoryImpl = Depends(get_book_repo)
) -> LangGraphRAGRepositoryImpl:
    """Creates RAG repository with injected dependencies."""
    return LangGraphRAGRepositoryImpl(
        vector_repo=vector_repo,
        chat_repo=chat_repo,
        books_repo=book_repo
    )
