from backend.src.application.interfaces.user_repository import UserRepository
from backend.src.domain.exceptions.user_exceptions import UserNotFound


def delete_user(user_repo: UserRepository, user_id: int) -> bool:
    if user_repo.get_by_id(user_id) is None:
        raise UserNotFound.by_id(user_id)
    return user_repo.delete(user_id=user_id)