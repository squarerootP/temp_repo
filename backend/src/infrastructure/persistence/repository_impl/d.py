import os
from typing import List

from langchain_chroma import Chroma
from langchain_core.documents import Document as LangchainDocument

from backend.src.application.interfaces.a_document_repository import \
    IVectorStoreRepository
from backend.src.domain.entities._document import DocumentChunk
from backend.src.infrastructure.adapters.rag.embedders.google_genai import \
    create_embeddings


class ChromaVectorStoreRepositoryImpl(IVectorStoreRepository):
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
        if not chunks:
            return 0
            
        # Convert to Langchain documents
        langchain_docs = []
        for chunk in chunks:
            langchain_docs.append(
                LangchainDocument(
                    page_content=chunk.page_content,
                    metadata=chunk.metadata
                )
            )
        
        # Add to vectorstore with explicit IDs
        ids = [chunk.id for chunk in chunks]
        self.vectorstore.add_documents(documents=langchain_docs, ids=ids)
        self.vectorstore.persist()  # type: ignore
        
        return len(chunks)
    
    def search_similar(self, query: str, k: int = 4) -> List[DocumentChunk]:
        """Search for similar chunks"""
        if not query:
            return []
            
        # Search the vectorstore
        results = self.vectorstore.similarity_search(query, k=k)
        
        # Convert back to DocumentChunk objects
        chunks = []
        for doc in results:
            chunk = DocumentChunk(
                id=doc.metadata.get("id", ""),  # The ID might be in metadata
                page_content=doc.page_content,
                metadata=doc.metadata
            )
            chunks.append(chunk)
            
        return chunks
    
    def delete_document_chunks(self, document_id: str) -> bool:
        """Delete all chunks for a document"""
        if not document_id:
            return False
            
        try:
            # Delete documents with matching document_id in metadata
            self.vectorstore.delete(
                where={"document_id": document_id}
            )
            self.vectorstore.persist()  # type: ignore
            return True
        except Exception:
            return False
    
    def get_chunk_count(self) -> int:
        """Get total number of chunks"""
        # Get collection stats to retrieve count
        collection = self.vectorstore._collection
        return collection.count()