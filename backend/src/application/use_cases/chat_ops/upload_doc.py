from typing import List, Optional

from backend.src.application.interfaces.rag_interfaces.document_repository import (
    IDocumentRepository, IVectorStoreRepository)
from backend.src.domain.entities.rag_entities.document import (Document,
                                                               DocumentChunk)
from logs.log_config import setup_logger

doc_logger = setup_logger("document")

class DocumentUploaderAndProcessor:
    """Coordinates document ingestion, embedding, and retrieval."""

    def __init__(self, doc_repo: IDocumentRepository, vector_repo: IVectorStoreRepository):
        self.doc_repo = doc_repo
        self.vector_repo = vector_repo

    def ingest_document(self, file_path: str, user_id: int) -> Document:
        """Add a document if new, or skip if already processed."""
        # Step 1: Process and hash
        document = self.doc_repo.process_document(file_path)
        
        document_hash = self.doc_repo.hash_document(document)

        # Step 2: Check for existing
        if self.doc_repo.document_exists(document_hash):
            doc_logger.info(f"Document with hash {document_hash} already exists. Skipping ingestion.")
            return self.doc_repo.get_document_by_hash(document_hash) #type: ignore

        doc_logger.info(f"Ingesting new document: {document.title} with hash {document_hash}")
        
        # Step 3: Chunk and embed
        chunks = self.doc_repo.chunk_document(document)
        num_added = self.vector_repo.add_chunks(chunks)
        
        document.user_id = user_id

        # Step 4: Save metadata
        saved_doc = self.doc_repo.save_document(document)
        print(f"Document {saved_doc.title} saved with {num_added} chunks.")
        return saved_doc

