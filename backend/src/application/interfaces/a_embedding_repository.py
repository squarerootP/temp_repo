from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from backend.src.domain.entities.document import (  # assuming these exist
    Document, VectorEmbedding)


class IEmbeddingRepository(ABC):
    """Interface for managing and generating embeddings."""

    @abstractmethod
    def save_embedding(self, document: Document, embedding: VectorEmbedding) -> None:
        """Persist a generated embedding associated with a document."""
        pass

    @abstractmethod
    def get_embedding(self, doc_hash: str) -> Optional[VectorEmbedding]:
        """Retrieve a stored embedding by the document hash."""
        pass

    @abstractmethod
    def generate_embedding(self, text: str, model: Optional[str] = None) -> List[float]:
        """Generate an embedding vector for the given text using a specified model."""
        pass
