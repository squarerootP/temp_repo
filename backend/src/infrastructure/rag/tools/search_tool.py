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

def search_web(query: str) -> str:
    """Search the web for up-to-date information"""
    return base_search.invoke(query)

search_tool = StructuredTool.from_function(
    func=search_web,
    name="tavily_search",
    description="Search the web for recent or missing information.",
    args_schema=SearchInput
)
