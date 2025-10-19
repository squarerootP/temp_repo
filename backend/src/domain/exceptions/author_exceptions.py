class AuthorNotFound(Exception):
    @classmethod
    def by_id(cls, author_id: int):
        return cls(f"Author with id {author_id} not found.")

    @classmethod
    def by_email(cls, email: str):
        return cls(f"Author with email {email} not found.")
