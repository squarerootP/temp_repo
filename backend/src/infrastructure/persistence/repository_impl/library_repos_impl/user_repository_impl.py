from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.src.application.interfaces.library_interfaces.user_repository import \
    UserRepository
from backend.src.domain.entities.library_entities.user import User
from backend.src.domain.services.utils import get_password_hash
from backend.src.infrastructure.adapters.mappers.library_mapper.user_mapper import \
    UserMapper
from backend.src.infrastructure.persistence.models.normal_models import \
    UserModel


class UserRepositoryImpl(UserRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: dict) -> User:
        hashed_password = get_password_hash(user["password"])
        user_data = {**user, "hashed_password": hashed_password}
        user_data.pop("password", None)
        
        user_entity = User(**user_data)
        db_user = UserMapper.to_model(user_entity)
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return UserMapper.to_entity(db_user)

    def get_by_id(self, user_id: int) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.user_id == user_id).first()
        return UserMapper.to_entity(db_user) if db_user else None

    def get_by_email(self, email: str) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.email == email).first()
        return UserMapper.to_entity(db_user) if db_user else None

    def get_by_phone(self, phone: str) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.phone == phone).first()
        return UserMapper.to_entity(db_user) if db_user else None

    def list(self, skip: Optional[int|None] = 0, limit: Optional[int|None] = 100) -> List[User]:
        db_users = self.db.query(UserModel).offset(skip).limit(limit).all()
        return [UserMapper.to_entity(user) for user in db_users]

    def search(self, text_to_search: str, skip: Optional[int|None] = 0, limit: Optional[int|None] = 100) -> List[User]:
        search_pattern = f"%{text_to_search}%"
        query = self.db.query(UserModel).filter(
            or_(
                UserModel.first_name.ilike(search_pattern),
                UserModel.second_name.ilike(search_pattern),
                UserModel.email.ilike(search_pattern),
            )
        )
        db_users = query.offset(skip).limit(limit).all()
        return [UserMapper.to_entity(user) for user in db_users]

    def update(self, user_id: int, user: dict) -> Optional[User]:
        db_user = self.db.query(UserModel).filter(UserModel.user_id == user_id).first()
        
        if not db_user:
            return None

        user_data = user.copy()
        if "password" in user_data:
            user_data["hashed_password"] = get_password_hash(user_data["password"])
            del user_data["password"]

        for key, value in user_data.items():
            setattr(db_user, key, value)

        self.db.commit()
        self.db.refresh(db_user)
        
        return UserMapper.to_entity(db_user)

    def delete(self, user_id: int) -> bool:
        db_user = self.db.query(UserModel).filter(UserModel.user_id == user_id).first()
        
        if not db_user:
            return False
            
        self.db.delete(db_user)
        self.db.commit()
        return True