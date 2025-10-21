from abc import ABC, abstractmethod
from typing import List, Optional
class IEmbeddingRepository(ABC):
    @abstractmethod
    def save_embedding(self, docs: dict, embeddings: List[float] ) -> None:
        pass

    @abstractmethod
    def get_embedding(self, doc_hash: str) -> Optional[List[float]]:
        pass
    
    @abstractmethod
    def generate_embedding(self, text: str) -> List[float]:
        pass