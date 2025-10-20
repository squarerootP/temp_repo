class AuthorNotFound(Exception):
    @classmethod
    def by_id(cls, author_id: int):
        return cls(f"Author with id {author_id} not found.")

    @classmethod
    def by_email(cls, email: str):
        return cls(f"Author with email {email} not found.")
class AuthorEmailAlreadyRegistered(Exception):
    def __init__(self, message: str):
        super().__init__(f"Author email already registered: {message}")
        
class AuthorInvalidData(Exception):
    def __init__(self, message: str):
        super().__init__(f"Invalid author data: {message}")

