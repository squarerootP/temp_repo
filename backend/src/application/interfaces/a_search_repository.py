from abc import ABC, abstractmethod


class ISearchRepository:
    @abstractmethod
    def search(self, query: str, num_results: int) -> list:
        """Perform a search with the given query and return results."""
        pass