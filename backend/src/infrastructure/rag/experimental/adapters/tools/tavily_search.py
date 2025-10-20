import os

from langchain_tavily import TavilySearch

from backend.rag_sys.src.infrastructure.settings import env_settings

tavily_api_key = env_settings.TAVILY_API_KEY
search_tool = TavilySearch(max_results=2, tavily_api_key=tavily_api_key)
