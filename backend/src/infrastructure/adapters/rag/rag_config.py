import os
import logging
from pathlib import Path
from typing import Set, Dict, Any

from pydantic_settings import BaseSettings, SettingsConfigDict

# Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")
logger = logging.getLogger(__name__)

class RAGSettings(BaseSettings):
    # Required settings
    CHROMA_PERSIST_DIR: str
    TEXT_FILES_DIR: str
    TAVILY_API_KEY: str
    GOOGLE_EMBEDDING_MODEL: str
    LLM_MODEL: str
    CEREBRAS_API_KEY: str
    GOOGLE_API_KEY: str

    # Optional settings with defaults
    MAX_FILE_SIZE_MB: int = 5
    ALLOWED_EXTENSIONS: Set[str] = {".txt", ".pdf", ".docx", ".md", ".csv"}

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding='utf-8',
        extra='ignore'  
    )

    def validate_config(self) -> bool:
        """Validate all configuration settings at once"""
        errors = []
        
        # Check required API keys
        for key in ["CEREBRAS_API_KEY", "GOOGLE_API_KEY", "TAVILY_API_KEY"]:
            if not getattr(self, key):
                errors.append(f"Missing {key}")
                
        # Check directories
        for dir_path in [self.CHROMA_PERSIST_DIR, self.TEXT_FILES_DIR]:
            if not os.path.exists(dir_path):
                try:
                    Path(dir_path).mkdir(parents=True, exist_ok=True)
                    logger.info(f"Created directory: {dir_path}")
                except Exception as e:
                    errors.append(f"Cannot create {dir_path}: {str(e)}")
        
        # Check file size limit
        if self.MAX_FILE_SIZE_MB <= 0:
            errors.append("MAX_FILE_SIZE_MB must be positive")
            
        if errors:
            raise ValueError(f"Configuration validation failed: {', '.join(errors)}")
            
        return True

    def validate_file(self, filename: str, size_bytes: int) -> Dict[str, Any]:
        """Validate if a file meets requirements for processing"""
        # Quick validation
        if not filename or size_bytes <= 0:
            return {"valid": False, "error": "Invalid file parameters"}
            
        # Extension check
        ext = os.path.splitext(filename.lower())[1]
        if ext not in self.ALLOWED_EXTENSIONS:
            return {"valid": False, "error": f"Unsupported file type: {ext}"}
            
        # Size check (convert bytes to MB)
        size_mb = size_bytes / (1024 * 1024)
        if size_mb > self.MAX_FILE_SIZE_MB:
            return {"valid": False, "error": f"File too large: {size_mb:.1f}MB (max {self.MAX_FILE_SIZE_MB}MB)"}
            
        return {"valid": True}


# Create settings instance
try:
    rag_settings = RAGSettings() #type: ignore
    # Validate on startup
    rag_settings.validate_config()
except Exception as e:
    logger.error(f"RAG configuration error: {str(e)}")
    raise