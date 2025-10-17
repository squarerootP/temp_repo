import os

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE_PATH = os.path.join(BASE_DIR, ".env")
print(ENV_FILE_PATH)
class Settings(BaseSettings):
    CEREBRAS_API_KEY: str
    GOOGLEAI_API_KEY: str
    LLM_MODEL: str
    TAVILY_API_KEY: str
    HUGGINGFACE_TOKEN: str

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding='utf-8'
    )

env_settings = Settings()