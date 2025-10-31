from typing import List

from backend.src.application.interfaces.library_interfaces.user_repository import \
    UserRepository
from backend.src.domain.entities.library_entities.user import User
from backend.src.domain.exceptions.user_exceptions import UserNotFound


class GetUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    # User sees its own info
    def get_user_me(self, current_user: User) -> User:
        return current_user

    # Helpers
    def get_user_by_email(self, email: str) -> User:
        user = self.user_repo.get_by_email(email)
        if user is None:
            raise UserNotFound.by_email(email)
        return user

    def get_user_by_phone(self, phone: str) -> User:
        user = self.user_repo.get_by_phone(phone)
        if user is None:
            raise UserNotFound.by_phone(phone)
        return user

    # Admin only
    def get_users(
        self, current_user: User, skip: int = 0, limit: int = 100
    ) -> List[User]:
        if current_user.role != "admin":
            raise PermissionError("You do not have permission to view all users.")
        return self.user_repo.list(skip=skip, limit=limit)
