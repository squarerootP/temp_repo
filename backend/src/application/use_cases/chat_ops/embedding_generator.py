from backend.src.application.interfaces.embedding_repository import IEmbeddingRepository
from typing import List
from backend.src.infrastructure.config.settings import APISettings

class EmbeddingGenerator:
    def __init__(self, embedding_repo: IEmbeddingRepository, config: APISettings):
        self.embedding_repository = embedding_repo
        self.config = config
        
    def generate_embedding(self, text: str) -> List[float]:
        embedding = self.embedding_repository.generate_embedding(text)
        return embedding
    
    def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            embedding = self.generate_embedding(text)
            embeddings.append(embedding)
        return embeddings