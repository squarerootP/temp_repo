from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Literal, Optional

Role = Literal["member", "admin"]


@dataclass
class User:
    user_id: Optional[int] = None
    user_name: str = ""
    first_name: str = ""
    second_name: str = ""
    email: str = ""
    phone: Optional[str] = None
    password: str = ""
    hashed_password: str = ""
    role: Role = "member"
