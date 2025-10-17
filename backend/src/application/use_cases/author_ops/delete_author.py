from sqlalchemy.orm import Session

from backend.src.application.use_cases import author_ops
from backend.src.infrastructure.persistence.author_repository_impl import AuthorRepository

def delete_author(author_repo: AuthorRepository, author_id: int) -> bool:
    return author_repo.delete(author_id)