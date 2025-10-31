from backend.src.domain.entities.library_entities.user import User
from backend.src.infrastructure.persistence.models.normal_models import \
    UserModel


class UserMapper:
    @staticmethod
    def to_entity(model: "UserModel") -> User:
        return User(
            user_id=model.user_id,
            user_name=model.user_name,
            first_name=model.first_name,
            second_name=model.second_name,
            email=model.email,
            phone=model.phone,
            hashed_password=model.hashed_password,
            role=model.role,
        )

    @staticmethod
    def to_model(entity: User) -> "UserModel":
        return UserModel(
            user_name=entity.user_name,
            first_name=entity.first_name,
            second_name=entity.second_name,
            email=entity.email,
            phone=entity.phone,
            hashed_password=entity.hashed_password,
            role=entity.role,
        )
