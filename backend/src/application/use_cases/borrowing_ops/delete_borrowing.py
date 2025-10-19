from backend.src.application.interfaces.borrowing_repository import \
    BorrowingRepository


def delete_borrowing(borrowing_repo: BorrowingRepository, borrow_id: int) -> bool:
    if borrowing_repo.get_by_id(borrow_id) is None:
        raise ValueError("Borrowing record not found")
    return borrowing_repo.delete(borrow_id)