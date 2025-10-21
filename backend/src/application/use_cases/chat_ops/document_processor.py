from backend.src.domain.entities.rag_entities import Document
from backend.src.application.interfaces.document_repository import IDocumentRepository

class DocumentProcessor:
    def __init__(self, document_repo: IDocumentRepository):
        self.document_repository = document_repo
        
    def process_document(self, file_path: str) -> Document:
        processed_document = self.document_repository.process_document(file_path)
        return processed_document
    
    def chunk_document(self, document: Document) -> list:
        chunks = self.document_repository.chunk_document(document)
        return chunks
    
    def hash_document(self, document_repo: IDocumentRepository,
        document: Document) -> str:
        hash = self.document_repository.hash_document(document)
        return hash