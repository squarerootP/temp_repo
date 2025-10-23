import os
from typing import List

from langchain_chroma import Chroma
from langchain_core.documents import Document as LangchainDocument

from backend.src.application.interfaces.a_document_repository import \
    IVectorStoreRepository
from backend.src.domain.entities._document import Document, DocumentChunk
from backend.src.infrastructure.adapters.rag.embedders.google_genai import \
    create_embeddings
from backend.src.application.interfaces.a_document_repository import \
    IDocumentRepository
class DocumentRepositoryImpl(IDocumentRepository):

    """Concrete implementation using Chroma DB"""
    
    # def __init__(self, persist_directory: str = r"./chroma_db"):
    #     os.makedirs(persist_directory, exist_ok=True)
    #     self.persist_directory = persist_directory
    #     self.embeddings = create_embeddings()
    #     self.vectorstore = self._load_vectorstore()
    
    def get_all_documents(self) -> List[Document]:
        return super().get_all_documents()
    def save_document(self, document: Document) -> Document:
        return super().save_document(document)
    def get_document_by_hash(self, content_hash: str) -> Document | None:
        return super().get_document_by_hash(content_hash)
    def delete_document(self, document_hash: str) -> bool:
        return super().delete_document(document_hash)
    def document_exists(self, content_hash: str) -> bool:
        return super().document_exists(content_hash)
    def hash_document(self, document: Document) -> str:
        return super().hash_document(document)
    def process_document(self, file_path: str) -> Document:
        return super().process_document(file_path)
    def chunk_document(self, document: Document) -> List[DocumentChunk]:
        return super().chunk_document(document)
    