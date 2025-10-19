from typing import List

from backend.src.application.interfaces.user_repository import UserRepository
from backend.src.domain.entities.user import User


def search_user(user_repo: UserRepository, text_to_search: str, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Searches for books by title, ISBN, genre, summary, or author name.
    This uses a single, efficient query.
    """
    return user_repo.search(text_to_search=text_to_search, skip=skip, limit=limit)