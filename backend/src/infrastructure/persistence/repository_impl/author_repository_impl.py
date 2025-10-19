from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.src.application.interfaces.author_repository import \
    AuthorRepository
from backend.src.domain.entities.author import Author


class AuthorRepositoryImpl(AuthorRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, author: Author) -> Author:
        self.db.add(author)
        self.db.commit()
        self.db.refresh(author)
        return author

    def get_by_id(self, author_id: int) -> Optional[Author]:
        return self.db.query(Author).filter(Author.author_id == author_id).first() #type: ignore

    def get_by_email(self, email: str) -> Optional[Author]:
        return self.db.query(Author).filter(Author.email == email).first() #type: ignore

    def list(self, skip: int = 0, limit: int = 100) -> List[Author]:
        return self.db.query(Author).offset(skip).limit(limit).all()

    def search(self, text_to_search: str, skip: int = 0, limit: int = 100) -> List[Author]:
        search_pattern = f"%{text_to_search}%"
        query = self.db.query(Author).filter(
            or_(
                Author.first_name.ilike(search_pattern), #type: ignore
                Author.last_name.ilike(search_pattern), #type: ignore
                Author.email.ilike(search_pattern), #type: ignore
            ) 
        )
        return query.offset(skip).limit(limit).all()

    def update(self, author_id: int, author: dict) -> Optional[Author]:
        db_author = self.get_by_id(author_id)
        if not db_author:
            return None

        author_data = author
        for key, value in author_data.items():
            setattr(db_author, key, value)
        
        self.db.commit()
        self.db.refresh(db_author)
        return db_author

    def delete(self, author_id: int) -> bool:
        db_author = self.get_by_id(author_id)
        if not db_author:
            return False
        self.db.delete(db_author)
        self.db.commit()
        return True