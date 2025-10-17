from typing import List

from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.src.domain.entities.models import Author
from backend.src.infrastructure.persistence.author_repository_impl import AuthorRepository

def search_authors(author_repo: AuthorRepository, text_to_search: str, skip: int = 0, limit: int = 100) -> List[Author]:
    return author_repo.search(text_to_search, skip, limit)