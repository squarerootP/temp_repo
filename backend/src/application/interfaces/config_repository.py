from typing import Protocol


class AppConfig(Protocol):
    GOOGLE_API_KEY: str
    GOOGLE_EMBEDDING_MODEL: str
    