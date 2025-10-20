from typing import List, Optional

from backend.src.application.interfaces.user_repository import UserRepository
from backend.src.domain.entities.user import User
from backend.src.domain.exceptions.user_exceptions import UserNotFound


def get_user_by_id(user_repo: UserRepository, user_id: int) -> User:
    user = user_repo.get_by_id(user_id)
    if user is None:
        raise UserNotFound.by_id(user_id)
    return user

def get_user_by_email(user_repo: UserRepository, email: str) -> User:
    user = user_repo.get_by_email(email)
    if user is None:
        raise UserNotFound.by_email(email)
    return user

def get_user_by_phone(user_repo: UserRepository, phone: str) -> User:
    user = user_repo.get_by_phone(phone)
    if user is None:
        raise UserNotFound.by_phone(phone)
    return user
              
def get_users(user_repo: UserRepository, skip: int = 0, limit: int = 100) -> List[User]:
    return user_repo.list(skip=skip, limit=limit)
