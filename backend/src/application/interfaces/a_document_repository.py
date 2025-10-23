from abc import ABC, abstractmethod
from typing import List, Optional

from backend.src.domain.entities._document import Document, DocumentChunk


# -------------------------------------------------------------------------
# Document Repository Interface
# -------------------------------------------------------------------------
class IDocumentRepository(ABC):
    """Abstract repository for managing raw documents and their metadata."""

    @abstractmethod
    def save_document(self, document: Document) -> Document:
        """Persist a document and return the saved entity."""
        pass

    @abstractmethod
    def get_document_by_hash(self, content_hash: str) -> Optional[Document]:
        """Retrieve a document by its unique content hash."""
        pass

    @abstractmethod
    def get_all_documents(self) -> List[Document]:
        """Return all stored documents (without chunk content)."""
        pass

    @abstractmethod
    def delete_document(self, document_hash: str) -> bool:
        """Delete a document and return True if successful."""
        pass

    @abstractmethod
    def document_exists(self, content_hash: str) -> bool:
        """Check if a document already exists by hash."""
        pass

    @abstractmethod
    def hash_document(self, document: Document) -> str:
        """Generate and return a SHA-based hash of the document content."""
        pass

    @abstractmethod
    def process_document(self, file_path: str) -> Document:
        """Extract text and metadata from a document file."""
        pass

    @abstractmethod
    def chunk_document(self, document: Document) -> List[DocumentChunk]:
        """Split a document into smaller chunks suitable for embedding."""
        pass


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
