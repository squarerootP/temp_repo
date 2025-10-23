from backend.src.domain.entities.borrowing import BorrowingManager
from backend.src.infrastructure.persistence.models.normal_models import BorrowingManagerModel


class BorrowingManagerMapper:
    @staticmethod
    def to_entity(model: "BorrowingManagerModel") -> BorrowingManager:
        return BorrowingManager(
            borrow_id=model.borrow_id,
            user_id=model.user_id,
            book_isbn=model.book_isbn,
            borrow_date=model.borrow_date,
            due_date=model.due_date,
            status=model.status,
        )

    @staticmethod
    def to_model(entity: BorrowingManager) -> "BorrowingManagerModel":
        return BorrowingManagerModel(
            borrow_id=entity.borrow_id,
            user_id=entity.user_id,
            book_isbn=entity.book_isbn,
            borrow_date=entity.borrow_date,
            due_date=entity.due_date,
            status=entity.status,
        )
