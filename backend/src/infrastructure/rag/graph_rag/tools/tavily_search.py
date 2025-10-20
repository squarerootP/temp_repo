from langchain_tavily import TavilySearch

from backend.src.infrastructure.config.settings import api_settings

tavily_api_key = api_settings.TAVILY_API_KEY
search_tool = TavilySearch(max_results=2, tavily_api_key=tavily_api_key)
