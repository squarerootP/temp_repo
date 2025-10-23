from typing import List
from backend.src.application.interfaces.a_search_repository import ISearchRepository

class SearchWeb:
    def __init__(self, search_repo: ISearchRepository):
        self.search_repo = search_repo
    def execute(self, query: str, num_results: int = 5) -> List[str]:
        """Perform a web search and return the top results."""
        results = self.search_repo.search(query, num_results)
        return results