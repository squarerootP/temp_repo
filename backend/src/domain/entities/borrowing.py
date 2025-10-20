from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional

Status = Literal["borrowed", "returned", "overdue"]

@dataclass
class BorrowingManager:

    user_id: int | None = None
    book_isbn: str = ""
    borrow_id: Optional[int] = None
    borrow_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    status: Status = "borrowed"