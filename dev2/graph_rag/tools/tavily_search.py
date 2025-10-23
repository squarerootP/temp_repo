# backend/src/infrastructure/rag/graph_rag/tools/tavily_search.py

from langchain_community.tools import TavilySearchResults
from backend.src.infrastructure.config.settings import api_settings

# This is a pre-built BaseTool object with the correct schema
# This replaces StructuredTool.from_function, SearchInput, and search_web
search_tool = TavilySearchResults(
    max_results=2,
    tavily_api_key=api_settings.TAVILY_API_KEY,
    name="tavily_search" # Ensure the name matches your prompt and graph
)