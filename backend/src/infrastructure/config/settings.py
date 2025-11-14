# backend\\src\\infrastructure\\configurations\\config.py
import os
from typing import Set

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")


class Settings(BaseSettings):
    RATE_LIMIT: int
    RATE_LIMIT_WINDOW_SIZE: int
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    APP_VERSION: str
    MAX_HISTORY_MSG_LEN_TO_RETRIEVE: int
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH, env_file_encoding="utf-8", extra="ignore"
    )


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
    CHUNK_SIZE: int
    CHUNK_OVERLAP: int
    NUM_DOCS_RETRIEVED: int
    SUMMARY_TOP_K: int

    # Optional settings with defaults
    MAX_FILE_SIZE_MB: int = 5
    ALLOWED_EXTENSIONS: Set[str] = {".txt"}

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH, env_file_encoding="utf-8", extra="ignore"
    )


class DBSettings(BaseSettings):
    DATABASE_URL: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH, env_file_encoding="utf-8", extra="ignore"
    )


class APISettings(BaseSettings):
    GOOGLE_API_KEY: str
    CEREBRAS_API_KEY: str
    TAVILY_API_KEY: str
    GOOGLE_EMBEDDING_MODEL: str
    LLM_MODEL: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH, env_file_encoding="utf-8", extra="ignore"
    )


api_settings = APISettings()  # type: ignore
rag_settings = RAGSettings()  # type: ignore
db_settings = DBSettings()  # type: ignore
settings = Settings()  # type: ignore
