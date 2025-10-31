from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from backend.src.domain.entities.rag_entities.document import Document


# -------------------------------------------------------------------------
# Document Repository Interface
# -------------------------------------------------------------------------
class IDocumentRepository(ABC):
    # Core document CRUD (SQL)
    def __init__(self) -> None:
        self.processed_documents: Dict[str, Dict[str, Any]] = {}
        pass

    def save_document(self, document: Document) -> Document: ...
    def get_document_by_hash(self, content_hash: str) -> Optional[Document]: ...
    def get_all_documents(self) -> List[Document]: ...  # NOT YET USED
    def delete_document(self, document_hash: str) -> bool: ...  # NOT YET USED
    def document_exists(self, content_hash: str) -> bool: ...
