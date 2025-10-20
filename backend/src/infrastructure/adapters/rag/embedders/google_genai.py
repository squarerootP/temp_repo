from functools import lru_cache

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from backend.src.application.interfaces.config_repository import AppConfig


@lru_cache(maxsize=4)
def _create_embeddings_cached(model: str, api_key: str) -> GoogleGenerativeAIEmbeddings:
    print("Creating embedding model instance (cached)")
    return GoogleGenerativeAIEmbeddings(
        model=f"models/{model}",
        google_api_key=api_key,  # type: ignore
        task_type="retrieval_document",
    )

def create_embeddings(cfg: AppConfig) -> GoogleGenerativeAIEmbeddings:
    return _create_embeddings_cached(cfg.GOOGLE_EMBEDDING_MODEL, cfg.GOOGLE_API_KEY)