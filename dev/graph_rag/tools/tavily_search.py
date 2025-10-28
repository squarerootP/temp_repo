"""
Tool for Tavily web search integration with LangGraph.
Uses standardized tool format from LangChain for compatibility.
"""
from typing import Any

from langchain.tools import Tool
from langchain_community.tools import TavilySearchResults
from langchain_tavily import TavilySearch
from pydantic import BaseModel, Field

from backend.src.infrastructure.config.settings import api_settings


class TavilyInput(BaseModel):
    query: str = Field(description="The search query for current events, news, or general knowledge.")
# Create a Tavily search tool with proper schema
_search = TavilySearchResults(
    max_results=2, 
    tavily_api_key=api_settings.TAVILY_API_KEY,
    args_schema=TavilyInput
)

# Define a simple search function that wraps the Tavily tool
def search_web(query: str) -> str:
    """Search the web for information."""
    print(f"Executing web search with query: '{query}'")
    print(f"DEBUG: search_web function called with query parameter: {query!r}")
    try:
        print(f"DEBUG: Invoking Tavily search with query: {query!r}")
        result = _search.invoke(query)
        print(f"DEBUG: Tavily search completed successfully")
        
        # Format the result for better readability
        if isinstance(result, str):
            print(f"DEBUG: Result is a string of length {len(result)}")
            return result
        elif isinstance(result, list):
            print(f"DEBUG: Result is a list with {len(result)} items")
            formatted_results = []
            for i, item in enumerate(result):
                formatted_results.append(f"[Search Result {i+1}]:\n{item}")
            return "\n\n".join(formatted_results)
        else:
            print(f"DEBUG: Result is of type {type(result)}")
            return f"Search Results:\n{result}"
            
    except Exception as e:
        print(f"Error in Tavily search: {e}")
        return f"Error searching the web: {str(e)}"

# Create a simplified wrapper tool
search_tool = Tool.from_function(
    name="tavily_search",
    description=(
        "A general web search tool (Tavily). "
        "Use this to find information on current events, news, or any general knowledge "
        "question that your local documents do not have an answer for."
    ),
    func=search_web,
    args_schema=TavilyInput,
)