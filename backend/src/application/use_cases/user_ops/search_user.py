from typing import List, Optional

from backend.src.application.interfaces.library_interfaces.user_repository import \
    UserRepository
from backend.src.domain.entities.library_entities.user import User


def search_user(user_repo: UserRepository, text_to_search: str, skip: Optional[int|None] = 0, limit: Optional[int | None] = 100) -> List[User]:
    """
    Searches for books by title, ISBN, genre, summary, or author name.
    This uses a single, efficient query.
    """
    return user_repo.search(text_to_search=text_to_search, skip=skip, limit=limit)