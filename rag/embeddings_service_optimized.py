import functools
import time

from config_optimized import Config
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from tenacity import retry, stop_after_attempt, wait_exponential


@functools.lru_cache(maxsize=1)
def create_embeddings():
    """Factory function to create embeddings with retry logic (singleton)"""
    
    @retry(
        stop=stop_after_attempt(Config.MAX_RETRIES),
        wait=wait_exponential(
            multiplier=1,
            min=Config.RETRY_MIN_WAIT,
            max=Config.RETRY_MAX_WAIT
        ),
        reraise=True
    )
    def _create_with_retry():
        print("   🔄 Creating embedding model instance...")
        start_time = time.time()
        
        embeddings = GoogleGenerativeAIEmbeddings(
            model=f"models/{Config.GOOGLE_EMBEDDING_MODEL}",
            google_api_key=Config.GOOGLE_API_KEY, #type: ignore
            task_type="retrieval_document"
        )
        
        # Test the embeddings
        test_result = embeddings.embed_query("test")
        
        init_time = time.time() - start_time
        print(f"   ✓ Embeddings initialized in {init_time:.2f}s (dim: {len(test_result)})")
        
        return embeddings
    
    try:
        return _create_with_retry()
    except Exception as e:
        print(f"   ✗ Failed to initialize embeddings after {Config.MAX_RETRIES} attempts: {e}")
        raise Exception(f"Embeddings initialization failed: {str(e)}")
