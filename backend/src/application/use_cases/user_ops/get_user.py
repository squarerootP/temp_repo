from typing import List, Optional

from backend.src.application.interfaces.user_repository import UserRepository
from backend.src.domain.entities.user import User


def get_user_by_id(user_repo: UserRepository, user_id: int) -> Optional[User]:
    if user_repo.get_by_id(user_id) is None:
        raise ValueError("User not found")
    return user_repo.get_by_id(user_id)
def get_user_by_email(user_repo: UserRepository, email: str) -> Optional[User]:
    if user_repo.get_by_email(email) is None:
        raise ValueError("User not found")
    return user_repo.get_by_email(email)
def get_user_by_phone(user_repo: UserRepository, phone: str) -> Optional[User]:
    if user_repo.get_by_phone(phone) is None:
        raise ValueError("User not found")
    return user_repo.get_by_phone(phone)                 
def get_users(user_repo: UserRepository, skip: int = 0, limit: int = 100) -> List[User]:
    return user_repo.list(skip=skip, limit=limit)
