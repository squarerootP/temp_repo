class BookNotFound(Exception):
    @classmethod
    def by_isbn(cls, book_isbn: str):
        return cls(f"Book with id {book_isbn} not found.")

    @classmethod
    def by_text(cls, text: str):
        return cls(f"No books found matching the text: {text}.")


class BookAlreadyExists(Exception):
    @classmethod
    def by_isbn(cls, book_isbn: str):
        return cls(f"Book with id {book_isbn} already exists.")
