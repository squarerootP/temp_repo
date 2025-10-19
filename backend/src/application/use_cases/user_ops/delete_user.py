from sqlalchemy.orm import Session

from backend.src.application.interfaces.user_repository import UserRepository
from backend.src.application.use_cases import user_ops


def delete_user(user_repo: UserRepository, user_id: int) -> bool:
    return user_repo.delete(user_id=user_id)