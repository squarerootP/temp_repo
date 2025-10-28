import logging
import os
from pathlib import Path
from typing import Any, Dict, Set

from pydantic_settings import BaseSettings, SettingsConfigDict

# Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")
ENV_FILE_PATH = r"C:\Users\Admin\workspace\phongnv37\backend\src\infrastructure\adapters\rag\.env"
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
    APP_VERSION: str 

    # Optional settings with defaults
    MAX_FILE_SIZE_MB: int = 5
    ALLOWED_EXTENSIONS: Set[str] = {".txt", ".pdf", ".docx", ".md", ".csv"}

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding='utf-8',
        extra='ignore'  
    )

# Create settings instance
try:
    rag_settings = RAGSettings() #type: ignore

except Exception as e:
    logger.error(f"RAG configuration error: {str(e)}")
    pass