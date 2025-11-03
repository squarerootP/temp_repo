from backend.src.application.interfaces.rag_interfaces.vectorstore_repo import \
    IVectorStoreRepository
from backend.src.domain.entities.rag_entities.document import Document
from typing import Dict, Any

class GetAllProcessedDocsUseCase:
    def __init__(self, vectorstore_repo: IVectorStoreRepository):
        self.vectorstore_repo = vectorstore_repo

    def execute(self) -> Dict[Any, Any]:
        return self.vectorstore_repo.get_all_processed_docs()
