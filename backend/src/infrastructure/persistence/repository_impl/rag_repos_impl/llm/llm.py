from typing import cast

from langchain_cerebras import ChatCerebras
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, SecretStr

from backend.src.infrastructure.config.settings import api_settings


class ToolCallerRequest(BaseModel):
    query: str = Field(description="The input query for the tool caller LLM")
    
def get_llm():
    """
    Initializes and returns the ChatCerebras LLM instance.
    Raises ValueError if the API key is not configured.
    """
    
    llm = ChatOpenAI(
        model="llama-3.1-8b",            # example model name
        api_key=api_settings.CEREBRAS_API_KEY, #type: ignore
        base_url="https://api.cerebras.ai/v1",
        temperature=0.1,  # Lower temperature for more consistent outputs
        model_kwargs={
            "response_format": {"type": "json_object"}  # Force JSON response format
        }
    )
    return llm

def get_normal_llm():
    llm = ChatOpenAI(
        model="llama-3.1-8b",            # example model name
        api_key=api_settings.CEREBRAS_API_KEY, #type: ignore
        base_url="https://api.cerebras.ai/v1",
        temperature=0.1, 
    )
    return llm

def get_tool_caller_llm():
    """
    Initializes and returns the ChatCerebras LLM instance configured for JSON output.
    Raises ValueError if the API key is not configured.
    """

    llm_caller = ChatCerebras(
        model="llama-3.1-8b",            # example model name
        api_key=api_settings.CEREBRAS_API_KEY, #type: ignore
        base_url="https://api.cerebras.ai/v1",
        temperature=0.1,  # Lower temperature for more consistent outputs
    )

# This block allows you to run this file directly to test it
if __name__ == "__main__":
    print("Attempting to create LLM instance...")
    try:
        llm_instance = get_llm()
        print("✅ LLM instance created successfully!")
        print(f"Model name: {llm_instance.model_name}")
    except ValueError as e:
        print(f"❌ Error: {e}") 