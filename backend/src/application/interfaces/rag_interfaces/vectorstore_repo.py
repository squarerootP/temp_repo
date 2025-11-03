from abc import ABC, abstractmethod
from typing import Any, List, Dict


class IVectorStoreRepository(ABC):
    @abstractmethod
    def process_document(self, file_path: str, hash: str, file_name: str) -> Any:
        pass

    @abstractmethod
    def get_similar_chunks(self, query: str, k: int = 4) -> List[Any]:
        pass

    @abstractmethod
    def delete_document_chunks(self, document_hash: str) -> bool:
        pass

    @abstractmethod
    def get_document_chunks(
        self, query: str, document_hash: str, k: int = 6
    ) -> List[Any]:
        pass

    @abstractmethod
    def get_all_processed_docs(self) -> Dict[Any, Any]:
        pass
