class UserNotFound(Exception):
    @classmethod
    def by_id(cls, user_id: int):
        return cls(f"User with id {user_id} not found.")

    @classmethod
    def by_email(cls, email: str):
        return cls(f"User with email {email} not found.")
    
    @classmethod
    def by_phone(cls, phone: str):
        return cls(f"User with phone {phone} not found.")
