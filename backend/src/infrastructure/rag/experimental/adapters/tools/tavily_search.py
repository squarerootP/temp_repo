import os

from backend.rag_sys.src.infrastructure.settings import env_settings

from langchain_tavily import TavilySearch

tavily_api_key = env_settings.TAVILY_API_KEY
search_tool = TavilySearch(max_results=2, tavily_api_key=tavily_api_key)
