from typing import Optional

from backend.src.application.interfaces.user_repository import UserRepository
from backend.src.domain.entities.user import User


def update_user(user_repo: UserRepository, user_id: int, data: dict) -> Optional[User]:
    user = user_repo.get_by_id(user_id=user_id)
    if not user:
        raise ValueError("User not found")
    user = data
    return user_repo.update(user_id, user)