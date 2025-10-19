from backend.src.application.interfaces.user_repository import UserRepository
from backend.src.domain.entities.models import User
from backend.src.presentation.schemas import user_schema


def create_user(user_repo: UserRepository, user: user_schema.UserCreate) -> User:
    return user_repo.create(user=user)