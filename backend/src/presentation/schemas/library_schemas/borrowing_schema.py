from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from .book_schema import BookResponse


class BorrowStatus(str, Enum):
    BORROWED = "borrowed"
    RETURNED = "returned"
    OVERDUE = "overdue"
class BorrowingBase(BaseModel):
    user_id: int
    book_isbn: str
    borrow_date: datetime = Field(default_factory=datetime.now)
    due_date: Optional[datetime] = None
    status: BorrowStatus = BorrowStatus.BORROWED

class BorrowingCreate(BorrowingBase):
    pass

class BorrowingUpdate(BaseModel):
    due_date: Optional[datetime] = None
    status: Optional[BorrowStatus] = None
class BorrowingResponse(BorrowingBase):
    borrow_id: int
    
    class ConfigDict:
        from_attributes = True
    
class BorrowingDetailResponse(BorrowingResponse):
    # user: UserResponse
    pass
    