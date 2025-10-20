from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field

from .borrowing_schema import BorrowingResponse


class UserRole(str, Enum):
    MEMBER = "member"
    STAFF = "staff"
    ADMIN = "admin"

class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    second_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    is_active: bool = True
    role: UserRole


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    class ConfigDict:
        from_attributes = True  

class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    second_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    password: Optional[str] = Field(None, min_length=8)

class UserResponse(UserBase):
    user_id: int
    is_active: bool = True
    created_at: datetime
    
    class ConfigDict:
        from_attributes = True

class UserDetailResponse(UserResponse):
    borrowings: List[BorrowingResponse] = []
    
