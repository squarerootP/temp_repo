import hashlib
from datetime import datetime
from typing import Any, Dict

from backend.src.application.interfaces.document_repository import \
    IDocumentRepository
from backend.src.domain.entities.document import Document


class UploadDocumentUseCase:
    """Use case for uploading and processing documents"""
    
    def __init__(self, document_repository: IDocumentRepository):
        self._document_repository = document_repository
    
    def execute(
        self, 
        filename: str, 
        content: bytes,
        metadata: Dict[str, Any] = None #type: ignore
    ) -> Dict[str, Any]:
        """
        Execute the upload document use case
        
        Returns:
            Dict with status, document, and whether it's a duplicate
        """
        # Calculate content hash
        content_hash = self._calculate_hash(content)
        
        # Check for duplicates
        existing_doc = self._document_repository.get_document_by_hash(content_hash)
        if existing_doc:
            return {
                "status": "duplicate",
                "document": existing_doc,
                "message": f"Document already exists (hash: {content_hash[:8]}...)"
            }
        
        # Create new document entity
        document = Document(
            id=content_hash,  # Using hash as ID for simplicity
            filename=filename,
            content_hash=content_hash,
            upload_time=datetime.now(),
            chunk_count=0,  # Will be updated after chunking
            file_size=len(content),
            metadata=metadata or {}
        )
        
        # Save document
        saved_doc = self._document_repository.save_document(document)
        
        return {
            "status": "success",
            "document": saved_doc,
            "message": "Document uploaded successfully",
            "content": content  # Pass content for further processing
        }
    
    @staticmethod
    def _calculate_hash(content: bytes) -> str:
        """Calculate SHA-256 hash of content"""
        return hashlib.sha256(content).hexdigest()