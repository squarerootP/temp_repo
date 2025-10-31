from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    MEMBER = "member"
    STAFF = "staff"
    ADMIN = "admin"


class UserBase(BaseModel):
    user_name: str = Field(..., min_length=1, max_length=50)
    first_name: str = Field(..., min_length=1, max_length=50)
    second_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    class ConfigDict:
        from_attributes = True


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    second_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    user_id: int

    class ConfigDict:
        from_attributes = True


class UserDetailResponse(UserResponse):
    pass
