from typing import cast

from langchain_cerebras import ChatCerebras
from pydantic import SecretStr

from backend.src.infrastructure.config.settings import api_settings


def get_llm():
    """
    Initializes and returns the ChatCerebras LLM instance.
    Raises ValueError if the API key is not configured.
    """
    cerebras_api_key = api_settings.CEREBRAS_API_KEY
    
    # It's good practice to check if the key exists
    if not cerebras_api_key:
        raise ValueError("CEREBRAS_API_KEY not found in settings.")

    llm = ChatCerebras(
        model=api_settings.LLM_MODEL,
        api_key=cast(SecretStr, cerebras_api_key),
        temperature=0.1,
    )
    return llm

