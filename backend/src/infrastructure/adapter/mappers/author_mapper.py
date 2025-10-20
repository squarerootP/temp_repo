from backend.src.domain.entities.author import Author
from backend.src.infrastructure.persistence.models import AuthorModel


class AuthorMapper:
    @staticmethod
    def to_entity(model: "AuthorModel") -> Author:
        return Author(
            author_id=model.author_id,
            first_name=model.first_name,
            last_name=model.last_name,
            email=model.email,
            biography=model.biography,
            book_isbns=[b.book_isbn for b in getattr(model, "books", [])],
        )

    @staticmethod
    def to_model(entity: Author) -> "AuthorModel":
        return AuthorModel(
            id=entity.author_id,
            first_name=entity.first_name,
            last_name=entity.last_name,
            email=entity.email,
            biography=entity.biography,
        )
