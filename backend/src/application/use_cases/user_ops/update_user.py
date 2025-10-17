from typing import Optional

from backend.src.application.interfaces.user_repository import UserRepository
from backend.src.domain.entities.models import User
from backend.src.presentation.schemas import user_schema


def update_user(user_repo: UserRepository, user_id: int, user: user_schema.UserUpdate) -> Optional[User]:
    return user_repo.update(user_id, user)