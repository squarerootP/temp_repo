import functools
import time
from typing import Any

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from rag.config_optimized import Config


@functools.lru_cache(maxsize=1)
def create_embeddings() -> Any:
    """
    Factory adapter for creating a singleton embedding client.
    Uses retry logic to handle transient initialization errors.
    """
    max_retries = Config.MAX_RETRIES
    wait_time = Config.RETRY_MIN_WAIT

    for attempt in range(1, max_retries + 1):
        try:
            start_time = time.time()

            embeddings = GoogleGenerativeAIEmbeddings(
                model=f"models/{Config.GOOGLE_EMBEDDING_MODEL}",
                google_api_key=Config.GOOGLE_API_KEY,  # type: ignore
                task_type="retrieval_document"
            )

            elapsed = time.time() - start_time
            print(f"✓ Embeddings model initialized in {elapsed:.2f}s")
            return embeddings

        except Exception as e:
            if attempt < max_retries:
                print(f"⚠️  Failed to initialize embeddings (attempt {attempt}/{max_retries}): {e}")
                time.sleep(wait_time)
                wait_time = min(wait_time * 2, Config.RETRY_MAX_WAIT)
            else:
                raise RuntimeError(f"❌ Failed to initialize embeddings after {max_retries} attempts") from e
