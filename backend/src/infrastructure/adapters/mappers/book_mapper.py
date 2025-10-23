from backend.src.domain.entities.book import Book
from backend.src.infrastructure.persistence.models.normal_models import BookModel


class BookMapper:
    @staticmethod
    def to_entity(model: "BookModel") -> Book:
        return Book(
            book_id = model.book_id,
            book_isbn=model.book_isbn,
            title=model.title,
            summary=model.summary,
            genre=model.genre,
            published_year=model.published_year,
            author_id=model.author_id,
            currently_borrowed_by=model.currently_borrowed_by,
            borrowing_ids=[b.borrow_id for b in getattr(model, "borrowings", [])],
        )

    @staticmethod
    def to_model(entity: Book) -> "BookModel":
        return BookModel(
            book_id=entity.book_id,
            book_isbn=entity.book_isbn,
            title=entity.title,
            summary=entity.summary,
            genre=entity.genre,
            published_year=entity.published_year,
            author_id=entity.author_id,
            currently_borrowed_by=entity.currently_borrowed_by,
        )
