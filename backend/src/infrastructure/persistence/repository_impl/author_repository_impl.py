from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.src.application.interfaces.author_repository import \
    AuthorRepository
from backend.src.domain.entities.author import Author
from backend.src.infrastructure.adapters.mappers.author_mapper import \
    AuthorMapper
from backend.src.infrastructure.persistence.models.normal_models import AuthorModel


class AuthorRepositoryImpl(AuthorRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, author: Author) -> Author:
        db_author = AuthorMapper.to_model(author)
        self.db.add(db_author)
        self.db.commit()
        self.db.refresh(db_author)
        
        return AuthorMapper.to_entity(db_author)

    def get_by_id(self, author_id: int) -> Optional[Author]:
        db_author = self.db.query(AuthorModel).filter(AuthorModel.author_id == author_id).first()
        return AuthorMapper.to_entity(db_author) if db_author else None

    def get_by_email(self, email: str) -> Optional[Author]:
        db_author = self.db.query(AuthorModel).filter(AuthorModel.email == email).first()
        return AuthorMapper.to_entity(db_author) if db_author else None

    def list(self, skip: int = 0, limit: int = 100) -> List[Author]:
        db_authors = self.db.query(AuthorModel).offset(skip).limit(limit).all()
        return [AuthorMapper.to_entity(author) for author in db_authors]

    def search(self, text_to_search: str, skip: int = 0, limit: int = 100) -> List[Author]:
        search_pattern = f"%{text_to_search}%"
        query = self.db.query(AuthorModel).filter(
            or_(
                AuthorModel.first_name.ilike(search_pattern),
                AuthorModel.last_name.ilike(search_pattern),
                AuthorModel.email.ilike(search_pattern),
            ) 
        )
        db_authors = query.offset(skip).limit(limit).all()
        return [AuthorMapper.to_entity(author) for author in db_authors]

    def update(self, author_id: int, author: dict) -> Optional[Author]:
        db_author = self.db.query(AuthorModel).filter(AuthorModel.author_id == author_id).first()
        
        if not db_author:
            return None

        for key, value in author.items():
            setattr(db_author, key, value)
        
        self.db.commit()
        self.db.refresh(db_author)
        
        return AuthorMapper.to_entity(db_author)

    def delete(self, author_id: int) -> bool:
        db_author = self.db.query(AuthorModel).filter(AuthorModel.author_id == author_id).first()
        
        if not db_author:
            return False
            
        self.db.delete(db_author)
        self.db.commit()
        return True