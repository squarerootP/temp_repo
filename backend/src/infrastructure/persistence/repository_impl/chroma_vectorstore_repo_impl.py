from typing import List
import os

from langchain_chroma import Chroma
from langchain_core.documents import Document as LangchainDocument

from backend.src.application.interfaces.document_repository import IVectorStoreRepository
from backend.src.domain.entities.rag_entities import DocumentChunk
from backend.src.infrastructure.adapters.rag.embedders.google_genai import create_embeddings


class ChromaVectorStoreRepository(IVectorStoreRepository):
    """Concrete implementation using Chroma DB"""
    
    def __init__(self, persist_directory: str = r"./chroma_db"):
        os.makedirs(persist_directory, exist_ok=True)
        self.persist_directory = persist_directory
        self.embeddings = create_embeddings()
        self.vectorstore = self._load_vectorstore()
    
    def _load_vectorstore(self):
        """Load or create vectorstore"""
        return Chroma(
            persist_directory=self.persist_directory,
            embedding_function=self.embeddings
        )
    
    def add_chunks(self, chunks: List[DocumentChunk]) -> int:
        """Add document chunks to vector store"""
        # Convert to Langchain documents and add to vectorstore
        # Implementation
        return 1 # the number of chunks added to the vectorstore
        pass
    
    def search_similar(self, query: str, k: int = 4) -> List[DocumentChunk]:
        """Search for similar chunks"""
        # Implementation
        pass
    
    def delete_document_chunks(self, document_id: str) -> bool:
        """Delete all chunks for a document"""
        # Implementation
        pass
    
    def get_chunk_count(self) -> int:
        """Get total number of chunks"""
        # Implementation
        pass