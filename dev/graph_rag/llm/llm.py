# backend/src/infrastructure/rag/graph_rag/llm/llm.py

from typing import cast

# Import the standard OpenAI client instead of ChatCerebras
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

from backend.src.infrastructure.config.settings import api_settings


def get_llm():
    """
    Initializes and returns an LLM client configured for the Cerebras API.
    
    This uses the standard ChatOpenAI client and points it to the
    Cerebras API endpoint, bypassing potential bugs in the
    langchain-cerebras library.
    """
    cerebras_api_key = api_settings.CEREBRAS_API_KEY
    
    if not cerebras_api_key:
        raise ValueError("CEREBRAS_API_KEY not found in settings.")

    # NOTE: This is the standard Cerebras API endpoint.
    # You may need to confirm this URL in your Cerebras account dashboard.
    cerebras_api_base_url = "https://api.cerebras.ai/v1"

    llm = ChatOpenAI(
        model=api_settings.LLM_MODEL,
        api_key=cast(SecretStr, cerebras_api_key),
        base_url=cerebras_api_base_url,
        temperature=0.1,
    )
    return llm

# This block allows you to run this file directly to test it
if __name__ == "__main__":
    print("Attempting to create LLM instance using ChatOpenAI client...")
    try:
        llm_instance = get_llm()
        print("✅ LLM instance created successfully!")
        print(f"Model name: {llm_instance.model_name}")
        print(f"Targeting API Base: {llm_instance.client.base_url}")
    except Exception as e:
        print(f"❌ Error: {e}")