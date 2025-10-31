from backend.src.application.interfaces.library_interfaces.user_repository import \
    UserRepository
from backend.src.domain.entities.library_entities.user import User
from backend.src.domain.exceptions.user_exceptions import UserNotFound


class DeleteUserUseCase:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def execute(self, user_id: int, current_user: User) -> bool:
        if current_user.role != "admin" and current_user.user_id != user_id:
            raise PermissionError("You do not have permission to delete this user.")

        if self.user_repo.get_by_id(user_id) is None:
            raise UserNotFound.by_id(user_id)
        return self.user_repo.delete(user_id=user_id)
