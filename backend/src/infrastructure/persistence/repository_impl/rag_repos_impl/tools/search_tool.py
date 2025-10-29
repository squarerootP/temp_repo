from langchain.tools import StructuredTool
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field

from backend.src.infrastructure.config.settings import api_settings

tavily_api_key = api_settings.TAVILY_API_KEY

# Create the basic tavily search tool
base_search = TavilySearch(
    max_results=2,
    tavily_api_key=tavily_api_key,
)

class SearchInput(BaseModel):
    query: str = Field(description="The search query for Tavily web search")

from langchain_core.tools import tool


@tool("Search", return_direct=True, description="A general web search tool (Tavily). Use this to find information on current events, news, or any general knowledge question that your local documents do not have an answer for.", args_schema=SearchInput)
def search_web(query: str) -> str:
    """Search the web for up-to-date information"""
    return base_search.invoke(query)