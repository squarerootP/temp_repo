import os
from typing import List, Optional

from backend.src.application.interfaces.rag_interfaces.document_repository import \
    IDocumentRepository
from backend.src.application.interfaces.rag_interfaces.vectorstore_repo import \
    IVectorStoreRepository
from backend.src.domain.entities.rag_entities.document import Document
from backend.src.domain.exceptions.chat_exceptions import \
    DocumentAlreadyProcessed
from backend.src.infrastructure.adapters.document_hasher import DocumentHasher
from logs.log_config import setup_logger

doc_logger = setup_logger("document")

class AddAndProcessDocument:
    """Coordinates document ingestion, embedding, and retrieval."""

    def __init__(self, doc_repo: IDocumentRepository, vector_repo: IVectorStoreRepository):
        self.doc_repo = doc_repo
        self.vector_repo = vector_repo

    def add_documents(self, file_path: str, user_id: int) -> Document:
        """Add a document if new, or skip if already processed."""
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        document_hash = DocumentHasher.hash_file(file_path)
        
        # Check if document exists in database
        if self.doc_repo.document_exists(document_hash):
            doc_logger.info(f"Document with hash {document_hash} already exists")
            raise DocumentAlreadyProcessed(f"Document already exists with hash {document_hash}")
        
        # Process document through vector store
        document = self.vector_repo.process_document(file_path, document_hash)
        document.user_id = user_id

        # Save document metadata to database
        saved_doc = self.doc_repo.save_document(document)
        doc_logger.info(f"Successfully processed and saved document {document_hash}")

        return saved_doc