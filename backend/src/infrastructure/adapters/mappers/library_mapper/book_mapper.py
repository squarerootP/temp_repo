from backend.src.domain.entities.library_entities.book import Book
from backend.src.infrastructure.persistence.models.normal_models import \
    BookModel


class BookMapper:
    @staticmethod
    def to_entity(model: "BookModel") -> Book:
        return Book(
            book_isbn=model.book_isbn,
            title=model.title,
            summary=model.summary,
            genre=model.genre,
            published_year=model.published_year,
            author_name=model.author_name,
        )

    @staticmethod
    def to_model(entity: Book) -> "BookModel":
        return BookModel(
            book_isbn=entity.book_isbn,
            title=entity.title,
            summary=entity.summary,
            genre=entity.genre,
            published_year=entity.published_year,
            author_name=entity.author_name,
        )
