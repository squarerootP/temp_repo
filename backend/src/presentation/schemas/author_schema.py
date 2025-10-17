from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class AuthorBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    biography: Optional[str] = None

class AuthorCreate(AuthorBase):
    pass

class AuthorUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    biography: Optional[str] = None


class AuthorResponse(AuthorBase):
    author_id: int
    
    class ConfigDict:
        from_attributes = True
    
class AuthorDetailResponse(AuthorResponse):
    
    class ConfigDict:
        from_attributes = True