from typing import List, Optional
from backend.src.domain.entities.models import User
from backend.src.presentation.schemas import user_schema

class UserRepository:
    def create(self, user: user_schema.UserCreate) -> User:
        raise NotImplementedError

    def get_by_id(self, user_id: int) -> Optional[User]:
        raise NotImplementedError

    def get_by_email(self, email: str) -> Optional[User]:
        raise NotImplementedError

    def get_by_phone(self, phone: str) -> Optional[User]:
        raise NotImplementedError

    def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        raise NotImplementedError

    def search(self, text_to_search: str, skip: int = 0, limit: int = 100) -> List[User]:
        raise NotImplementedError

    def update(self, user_id: int, user: user_schema.UserUpdate) -> Optional[User]:
        raise NotImplementedError

    def delete(self, user_id: int) -> bool:
        raise NotImplementedError