from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Literal, Optional

Role = Literal["member", "admin"]

@dataclass
class User:
    user_id: int 
    first_name: str = ""
    second_name: str = ""
    email: str = ""
    phone: Optional[str] = None
    address: Optional[str] = None
    hashed_password: str = ""
    is_active: bool = True
    role: Role = "member"
    created_at: Optional[datetime] = None
    borrowing_ids: List[int] = field(default_factory=list)
    currently_borrowed_book_isbns: List[str] = field(default_factory=list)