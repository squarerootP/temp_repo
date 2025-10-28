# backend\\src\\infrastructure\\configurations\\config.py
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")

class Settings(BaseSettings):
    SECRET_KEY: str
    DATABASE_URL: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    RATE_LIMIT: int
    RATE_LIMIT_WINDOW_SIZE: int
    APP_VERSION: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding='utf-8',
        extra='ignore'   # 👈 allow unrelated keys
    )


class APISettings(BaseSettings):
    CEREBRAS_API_KEY: str
    GOOGLE_API_KEY: str
    TAVILY_API_KEY: str
    GOOGLE_EMBEDDING_MODEL: str
    LLM_MODEL: str
    OPENAI_API_KEY: str = ""  # Added with default empty string

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding='utf-8',
        extra='ignore'   # 👈 same here
    )

# settings = Settings()
api_settings = APISettings() #type: ignore

settings = Settings() #type: ignore

class Validator():
    
    CEREBRAS_API_KEY = ""
    GOOGLE_API_KEY = ""
    MAX_FILE_SIZE = 5
    ALLOWED_EXTENSIONS = ""
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
    
import logging
import os
from pathlib import Path
from typing import Any, Dict, Set

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