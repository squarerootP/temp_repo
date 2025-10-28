from abc import ABC, abstractmethod
from typing import List, Optional

from backend.src.domain.entities.rag_entities.document import (Document,
                                                               DocumentChunk)


# -------------------------------------------------------------------------
# Document Repository Interface
# -------------------------------------------------------------------------
class IDocumentRepository(ABC):
    # Core document CRUD (SQL)
    def save_document(self, document: Document) -> Document: ...
    def get_document_by_hash(self, content_hash: str) -> Optional[Document]: ...
    def get_all_documents(self) -> List[Document]: ...
    def delete_document(self, document_hash: str) -> bool: ...
    def document_exists(self, content_hash: str) -> bool: ...
    
    # Utilities (no storage)
    def hash_document(self, document: Document) -> str: ...
    def process_document(self, file_path: str) -> Document: ...
    def chunk_document(self, document: Document) -> List[DocumentChunk]: ...


class IVectorStoreRepository(ABC):
    """Abstract repository for vector store operations (Chroma, FAISS, etc.)."""

    @abstractmethod
    def add_chunks(self, chunks: List[DocumentChunk]) -> int:
        """Add chunks (and their embeddings) to the vector store. Returns count added."""
        pass

    @abstractmethod
    def search_similar(self, query: str, k: int = 4) -> List[DocumentChunk]:
        """Search the vector store for the top-k most similar chunks."""
        pass

    @abstractmethod
    def delete_document_chunks(self, document_id: str) -> bool:
        """Delete all chunks associated with a document."""
        pass

    @abstractmethod
    def get_chunk_count(self) -> int:
        """Return the total number of chunks currently stored."""
        pass
    @abstractmethod
    def list_documents_hashses(self) -> List[str]:
        """Return all document hashes in vector store."""
        pass
