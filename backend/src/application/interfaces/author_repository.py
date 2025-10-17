from typing import List, Optional
from backend.src.domain.entities.models import Author
from backend.src.presentation.schemas import author_schema

class AuthorRepository:
    def create(self, author: author_schema.AuthorCreate) -> Author:
        raise NotImplementedError

    def get_by_id(self, author_id: int) -> Optional[Author]:
        raise NotImplementedError

    def get_by_email(self, email: str) -> Optional[Author]:
        raise NotImplementedError

    def list(self, skip: int = 0, limit: int = 100) -> List[Author]:
        raise NotImplementedError

    def search(self, text_to_search: str, skip: int = 0, limit: int = 100) -> List[Author]:
        raise NotImplementedError

    def update(self, author_id: int, author: author_schema.AuthorUpdate) -> Optional[Author]:
        raise NotImplementedError

    def delete(self, author_id: int) -> bool:
        raise NotImplementedError