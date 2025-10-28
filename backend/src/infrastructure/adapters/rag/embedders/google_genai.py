import functools
import time
from typing import Any

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from backend.src.infrastructure.config.settings import rag_settings


@functools.lru_cache(maxsize=1)
def create_embeddings() -> Any:
    embeddings = GoogleGenerativeAIEmbeddings(
        model=f"models/{rag_settings.GOOGLE_EMBEDDING_MODEL}",
        google_api_key=rag_settings.GOOGLE_API_KEY,  # type: ignore
        task_type="retrieval_document")

    return embeddings
