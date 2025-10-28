from typing import cast

from langchain_cerebras import ChatCerebras
from pydantic import SecretStr

from backend.src.infrastructure.config.settings import rag_settings


def get_llm():
    """
    Initializes and returns the ChatCerebras LLM instance.
    Raises ValueError if the API key is not configured.
    """
    cerebras_api_key = rag_settings.CEREBRAS_API_KEY

    llm = ChatCerebras(
        model=rag_settings.LLM_MODEL,
        api_key=cast(SecretStr, cerebras_api_key),
        temperature=0.1,
    )
    return llm

