from backend.src.domain.entities.library_entities.user import User
from backend.src.infrastructure.persistence.models.normal_models import \
    UserModel


class UserMapper:
    @staticmethod
    def to_entity(model: "UserModel") -> User:
        return User(
            user_id=model.user_id,
            first_name=model.first_name,
            second_name=model.second_name,
            email=model.email,
            phone=model.phone,
            address=model.address,
            hashed_password=model.hashed_password,
            is_active=model.is_active,
            role=model.role,
            created_at=model.created_at,
            borrowing_ids=[b.borrow_id for b in getattr(model, "Borrowings", [])],
            currently_borrowed_book_isbns=[
                b.book_isbn for b in getattr(model, "borrowed_books", [])
            ],
        )

    @staticmethod
    def to_model(entity: User) -> "UserModel":
        return UserModel(
            user_id=entity.user_id,
            first_name=entity.first_name,
            second_name=entity.second_name,
            email=entity.email,
            phone=entity.phone,
            address=entity.address,
            hashed_password=entity.hashed_password,
            is_active=entity.is_active,
            role=entity.role,
            created_at=entity.created_at,
        )
