from langchain.tools import tool
from langchain_tavily import TavilySearch

from backend.src.infrastructure.config.settings import rag_settings

client = TavilySearch(api_key=rag_settings.TAVILY_API_KEY)
from typing import Any


@tool("tavily_search", return_direct=True, description="A general web search tool (Tavily). Use this to find information on current events, news, or any general knowledge question that your local documents do not have an answer for.")
def tavily_search(query: str) -> Any:
    """Search the web for information."""
    print(f"Executing web search with query: '{query}'")
    try:
        result = client.run(query)
        return result
    except Exception as e:
        print(f"Error in Tavily search: {e}")
        return f"Error searching the web: {str(e)}"
