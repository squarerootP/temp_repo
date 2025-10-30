from typing import List, Optional

from sqlalchemy.orm import Session

from backend.src.application.interfaces.rag_interfaces.document_repository import \
    IDocumentRepository
from backend.src.domain.entities.rag_entities.document import Document
from backend.src.infrastructure.adapters.mappers.rag_mappers.document_mapper import \
    DocumentMapper
from backend.src.infrastructure.persistence.models.rag_models import \
    DocumentModel
from logs.log_config import setup_logger

doc_logger = setup_logger("document_repo")

class DocumentRepositoryImpl(IDocumentRepository):
    """Handles document CRUD operations in the database."""

    def __init__(self, db: Session):
        self.db = db

    def get_all_documents(self) -> List[Document]:
        """Retrieve all documents."""
        db_docs = self.db.query(DocumentModel).all()
        return [DocumentMapper.to_entity(doc) for doc in db_docs]

    def save_document(self, document: Document) -> Document:
        """Persist a document entity to the database."""
        db_doc = DocumentMapper.to_model(document)
        self.db.add(db_doc)
        self.db.commit()
        self.db.refresh(db_doc)
        return DocumentMapper.to_entity(db_doc)

    def get_document_by_hash(self, content_hash: str) -> Optional[Document]:
        """Retrieve a document by its hash."""
        db_doc = (
            self.db.query(DocumentModel)
            .filter(DocumentModel.hash == content_hash)
            .first()
        )
        if not db_doc:
            doc_logger.info(f"No document found with hash {content_hash}")
        return DocumentMapper.to_entity(db_doc) if db_doc else None

    def delete_document(self, document_hash: str) -> bool:
        """Delete a document by its hash."""
        db_doc = (
            self.db.query(DocumentModel)
            .filter(DocumentModel.hash == document_hash)
            .first()
        )
        if not db_doc:
            doc_logger.info(f"No document found with hash {document_hash} to delete")
            return False
        
        self.db.delete(db_doc)
        self.db.commit()
        doc_logger.info(f"Deleted document with hash {document_hash}")
        return True

    def document_exists(self, content_hash: str) -> bool:
        """Check if a document exists by hash."""
        return (
            self.db.query(DocumentModel)
            .filter(DocumentModel.hash == content_hash)
            .first()
            is not None
        )