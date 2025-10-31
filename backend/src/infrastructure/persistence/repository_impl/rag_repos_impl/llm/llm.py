from typing import cast

from langchain_cerebras import ChatCerebras
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, SecretStr

from backend.src.infrastructure.config.settings import api_settings


class ToolCallerRequest(BaseModel):
    query: str = Field(description="The input query for the tool caller LLM")


def get_small_llm():
    """
    Initializes and returns the ChatCerebras LLM instance.
    Raises ValueError if the API key is not configured.
    """

    llm = ChatCerebras(
        model="llama3.1-8b",
        api_key=api_settings.CEREBRAS_API_KEY,  # type: ignore
        base_url="https://api.cerebras.ai/v1",
        temperature=0.1,
    )
    return llm


def get_big_llm():
    llm = ChatCerebras(
        model="llama-3.3-70b",
        api_key=api_settings.CEREBRAS_API_KEY,  # type: ignore
        base_url="https://api.cerebras.ai/v1",
        temperature=0.1,
    )
    return llm


def get_decent_llm():
    llm = ChatCerebras(
        model="llama-3.3-70b",
        api_key=api_settings.CEREBRAS_API_KEY,  # type: ignore
        base_url="https://api.cerebras.ai/v1",
        temperature=0.1,
    )
    return llm
