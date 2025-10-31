from typing import List, Optional

from backend.src.application.interfaces.library_interfaces.user_repository import \
    UserRepository
from backend.src.domain.entities.library_entities.user import User


class SearchUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(
        self,
        current_user: User,
        text_to_search: str,
        skip: Optional[int | None] = 0,
        limit: Optional[int | None] = 100,
    ) -> List[User]:
        if current_user.role != "admin":
            raise PermissionError("You do not have permission to search users.")

        return self.user_repo.search(
            text_to_search=text_to_search, skip=skip, limit=limit
        )
