from backend.src.application.interfaces.library_interfaces.author_repository import \
    AuthorRepository
from backend.src.domain.exceptions.author_exceptions import AuthorNotFound


def delete_author(author_repo: AuthorRepository, author_id: int) -> bool:
    if not author_repo.get_by_id(author_id=author_id):
        raise AuthorNotFound("There exists no author of such ID")
    
    return author_repo.delete(author_id)