from typing import Optional

from backend.src.domain.exceptions.author_exceptions import AuthorNotFound

from backend.src.domain.entities.author import Author
from backend.src.application.interfaces.author_repository import AuthorRepository



def update_author(author_repo: AuthorRepository, author_id: int, data: dict) -> Optional[Author]:
    author = author_repo.get_by_id(author_id=author_id)
    if not author:
        raise AuthorNotFound(f"Author with id {author_id} not found.")
    author = Author(**author)
    return author_repo.update(author_id, author)