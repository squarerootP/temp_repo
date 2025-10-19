from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.src.application.interfaces.user_repository import UserRepository
from backend.src.domain.entities.user import User
from backend.src.domain.services.utils import get_password_hash


class UserRepositoryImpl(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: dict) -> User:
        hashed_password = get_password_hash(user["password"])
        db_user = User(
            first_name=user["first_name"],
            second_name=user["second_name"],
            email=user["email"],
            phone=user["phone"],
            address=user["address"],
            hashed_password=hashed_password,
            is_active=True,
            role=user["role"]
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.user_id == user_id).first() #type: ignore

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first() #type: ignore

    def get_by_phone(self, phone: str) -> Optional[User]:
        return self.db.query(User).filter(User.phone == phone).first() #type: ignore

    def list(self, skip: int = 0, limit: int = 100) -> List[User]:
        return self.db.query(User).offset(skip).limit(limit).all()

    def search(self, text_to_search: str, skip: int = 0, limit: int = 100) -> List[User]:
        search_pattern = f"%{text_to_search}%"
        query = self.db.query(User).filter(
            or_(
                User.first_name.ilike(search_pattern), #type: ignore
                User.second_name.ilike(search_pattern), #type: ignore
                User.email.ilike(search_pattern), #type: ignore
            )
        )
        return query.offset(skip).limit(limit).all()

    def update(self, user_id: int, user: dict) -> Optional[User]:
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None

        user_data = user
        if "password" in user_data:
            user_data["hashed_password"] = get_password_hash(user_data["password"])
            del user_data["password"]

        for key, value in user_data.items():
            setattr(db_user, key, value)

        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete(self, user_id: int) -> bool:
        db_user = self.get_by_id(user_id)
        if not db_user:
            return False
        self.db.delete(db_user)
        self.db.commit()
        return True