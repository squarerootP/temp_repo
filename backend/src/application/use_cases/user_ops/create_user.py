from backend.src.application.interfaces.library_interfaces.user_repository import \
    UserRepository
from backend.src.domain.entities.library_entities.user import User


def create_user(user_repo: UserRepository, data: dict) -> User:
    """Business logic for creating a user."""
    # Check if user with the same email already exists
    if user_repo.get_by_email(data["email"]):
        raise ValueError("User email already registered")
    # Check if phone number is already registered
    if user_repo.get_by_phone(data["phone"]):
        raise ValueError("User phone number already registered")
    user = data
    return user_repo.create(user=user)