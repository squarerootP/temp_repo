from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from backend.src.domain.entities.rag_entities import Document, DocumentChunk


class IDocumentRepository(ABC):
    """Abstract repository for document operations"""
    
    @abstractmethod
    def save_document(self, document: Document) -> Document:
        """Save a document and return the saved entity"""
        pass
    
    @abstractmethod
    def get_document_by_hash(self, content_hash: str) -> Optional[Document]:
        """Retrieve document by content hash"""
        pass
    
    @abstractmethod
    def get_all_documents(self) -> Dict[str, Any]:
        """Get all documents"""
        pass
    
    @abstractmethod
    def delete_document(self, document_hash: str) -> bool:
        """Delete a document"""
        pass
    
    @abstractmethod
    def document_exists(self, content_hash: str) -> bool:
        """Check if document exists"""
        pass
    @abstractmethod
    def hash_document(self, document: Document) -> str:
        """Generate a hash for the document content"""
        pass
    @abstractmethod
    def process_document(self, file_path: str) -> Document:
        """Process and extract content from the document at file_path"""
        pass
    @abstractmethod
    def chunk_document(self, document: Document) -> List[DocumentChunk]:
        """Chunk the document into smaller pieces"""
        pass


class IVectorStoreRepository(ABC):
    """Abstract repository for vector store operations"""
    
    @abstractmethod
    def add_chunks(self, chunks: List[DocumentChunk]) -> int:
        """Add document chunks to vector store"""
        pass
    
    @abstractmethod
    def search_similar(self, query: str, k: int = 4) -> List[DocumentChunk]:
        """Search for similar chunks"""
        pass
    
    @abstractmethod
    def delete_document_chunks(self, document_id: str) -> bool:
        """Delete all chunks for a document"""
        pass
    
    @abstractmethod
    def get_chunk_count(self) -> int:
        """Get total number of chunks"""
        pass