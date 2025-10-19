from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional

Status = Literal["borrowed", "returned", "overdue"]

@dataclass
class BorrowingManager:
    borrow_id: Optional[int] = None
    user_id: int #type: ignore 
    book_isbn: str #type: ignore
    borrow_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    status: Status = "borrowed"