from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from backend.rag_sys.src.infrastructure.settings import env_settings

cerebras_api_key = env_settings.CEREBRAS_API_KEY
google_ai_embedder_api_key = env_settings.GOOGLEAI_API_KEY
llm_model = env_settings.LLM_MODEL

llm = ChatOpenAI(
    model = llm_model if llm_model else "llama-3.3-70b",
    api_key=SecretStr(cerebras_api_key) if cerebras_api_key else None,
    base_url="https://api.cerebras.ai/v1",
    temperature=0.0
)