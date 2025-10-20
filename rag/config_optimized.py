import os

from dotenv import load_dotenv

load_dotenv()

class Config:
    # Required API keys
    CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    
    # Embedding settings
    EMBEDDING_PROVIDER = "google"
    GOOGLE_EMBEDDING_MODEL = "text-embedding-004"
    
    # LLM settings
    LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
    LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2048"))
    
    # Document processing - OPTIMIZED
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1024"))  # Smaller for better retrieval
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "124"))  # 20% overlap
    
    # API settings
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10MB
    ALLOWED_EXTENSIONS = ['.pdf']
    
    # Performance settings
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "4"))
    VECTORSTORE_DIR = os.getenv("VECTORSTORE_DIR", "vectorstore")
    
    # Memory management
    MAX_CONTEXT_CHUNKS = int(os.getenv("MAX_CONTEXT_CHUNKS", "6"))
    BATCH_SIZE = int(os.getenv("BATCH_SIZE", "50"))  # Chunks per batch
    GC_AFTER_DOCUMENT_LOAD = os.getenv("GC_AFTER_DOCUMENT_LOAD", "true").lower() == "true"
    
    # Retry settings
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_MIN_WAIT = int(os.getenv("RETRY_MIN_WAIT", "2"))
    RETRY_MAX_WAIT = int(os.getenv("RETRY_MAX_WAIT", "10"))
    
    # Cache settings
    ENABLE_QUERY_CACHE = os.getenv("ENABLE_QUERY_CACHE", "true").lower() == "true"
    CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", "100"))
    CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))  # 1 hour
    
    @classmethod
    def validate(cls):
        """Validate configuration on startup"""
        missing_keys = []
        
        if not cls.CEREBRAS_API_KEY:
            missing_keys.append("CEREBRAS_API_KEY")
        if not cls.GOOGLE_API_KEY:
            missing_keys.append("GOOGLE_API_KEY")
            
        if missing_keys:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
        
        print("✓ Configuration validated successfully")
    
    @classmethod
    def validate_file_size(cls, size: int) -> bool:
        """Validate file size"""
        return 0 < size <= cls.MAX_FILE_SIZE
    
    @classmethod
    def validate_file_extension(cls, filename: str) -> bool:
        """Validate file extension"""
        if not filename:
            return False
        ext = os.path.splitext(filename.lower())[1]
        return ext in cls.ALLOWED_EXTENSIONS
    
    @classmethod
    def get_summary(cls) -> dict:
        """Get configuration summary"""
        return {
            "llm_model": cls.LLM_MODEL,
            "embedding_model": cls.GOOGLE_EMBEDDING_MODEL,
            "chunk_size": cls.CHUNK_SIZE,
            "chunk_overlap": cls.CHUNK_OVERLAP,
            "max_context_chunks": cls.MAX_CONTEXT_CHUNKS,
            "cache_enabled": cls.ENABLE_QUERY_CACHE,
            "max_file_size_mb": cls.MAX_FILE_SIZE / (1024 * 1024)
        }
