from typing import List, Optional
from backend.src.domain.entities._document import Document, DocumentChunk
from backend.src.application.interfaces.a_document_repository import IDocumentRepository, IVectorStoreRepository

class DocumentUploaderAndProcessor:
    """Coordinates document ingestion, embedding, and retrieval."""

    def __init__(self, doc_repo: IDocumentRepository, vector_repo: IVectorStoreRepository):
        self.doc_repo = doc_repo
        self.vector_repo = vector_repo

    def ingest_document(self, file_path: str) -> Optional[Document]:
        """Add a document if new, or skip if already processed."""
        # Step 1: Process and hash
        document = self.doc_repo.process_document(file_path)
        document_hash = self.doc_repo.hash_document(document)

        # Step 2: Check for existing
        if self.doc_repo.document_exists(document_hash):
            print(f"Document already exists (hash match): {file_path}")
            return self.doc_repo.get_document_by_hash(document_hash)

        # Step 3: Chunk and embed
        chunks = self.doc_repo.chunk_document(document)
        num_added = self.vector_repo.add_chunks(chunks)

        # Step 4: Save metadata
        saved_doc = self.doc_repo.save_document(document)
        print(f"Document {saved_doc.title} saved with {num_added} chunks.")
        return saved_doc

