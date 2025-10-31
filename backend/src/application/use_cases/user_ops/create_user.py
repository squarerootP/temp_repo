from backend.src.application.interfaces.library_interfaces.user_repository import \
    UserRepository
from backend.src.domain.entities.library_entities.user import User


class CreateUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, user: User) -> User:
        """Business logic for creating a user."""

        if self.user_repo.get_by_username(user.user_name):
            raise ValueError("Username already taken")
        if self.user_repo.get_by_email(user.email):
            raise ValueError("User email already registered")
        if self.user_repo.get_by_phone(user.phone):  # type: ignore
            raise ValueError("User phone number already registered")

        return self.user_repo.create(user=user)  
