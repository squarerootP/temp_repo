from typing import List

from backend.src.application.interfaces.author_repository import \
    AuthorRepository
from backend.src.domain.entities.author import Author
from backend.src.domain.exceptions.author_exceptions import AuthorNotFound


def search_authors(author_repo: AuthorRepository, text_to_search: str, skip: int = 0, limit: int = 100) -> List[Author]:
    author_lst = author_repo.search(text_to_search, skip, limit)
    if not author_lst:
        raise AuthorNotFound(f"No authors found matching '{text_to_search}'.")
    return author_repo.search(text_to_search, skip, limit)