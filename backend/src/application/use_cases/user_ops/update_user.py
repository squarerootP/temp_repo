from typing import Optional

from backend.src.application.interfaces.library_interfaces.user_repository import \
    UserRepository
from backend.src.domain.entities.library_entities.user import User


class UpdateUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, current_user: User, user_id: int, data: dict) -> Optional[User]:
        if current_user.user_id != user_id:
            raise PermissionError("You do not have permission to update this user.")

        db_user = self.user_repo.get_by_id(user_id=user_id)
        if not db_user:
            raise ValueError("User not found")

        if self.user_repo.get_by_email(
            data.get("email", "")
        ) and db_user.email != data.get("email", ""):
            raise ValueError("Email already in use")

        if self.user_repo.get_by_phone(
            data.get("phone", "")
        ) and db_user.phone != data.get("phone", ""):
            raise ValueError("Phone number already in use")

        if "user_name" in data:
            raise ValueError("Username cannot be changed")
        return self.user_repo.update(user_id, data)
