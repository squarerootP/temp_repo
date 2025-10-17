from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.application.use_cases import user_ops
from backend.src.domain.entities.models import User
from backend.src.infrastructure.persistence.database import get_db
from backend.src.infrastructure.web.auth_provider import (
    get_current_active_user, has_role)
from backend.src.presentation.schemas import user_schema
from backend.src.infrastructure.persistence.user_repository_impl import UserRepositoryImpl
router = APIRouter(
    prefix="/users", 
    tags=["Users"]  
)

@router.get("/me", response_model=user_schema.UserResponse)
def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Return the current user's simple information.
    """
    return current_user
@router.get("/", response_model=List[user_schema.UserResponse]) # R
def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(has_role("admin")),
    db: Session = Depends(get_db)
):
    """
    Retrieve all users, default to 0-100
    """
    user_repo = UserRepositoryImpl(db)
    users = user_ops.get_users(user_repo = user_repo,  skip=skip, limit=limit)
    return users

@router.get("", 
            response_model=List[user_schema.UserResponse]) # R
def search_users(text_to_search: str, 
                 skip: Optional[int] = 0,
                 limit: Optional[int] = 100,
                 db: Session = Depends(get_db)):
    """
    Retrieve all users with matching information, default to 0-100
    """
    user_repo = UserRepositoryImpl(db)
    users = user_ops.search_user(user_repo = user_repo,  text_to_search=text_to_search, skip=skip, limit=limit)
    return users
@router.get("/{user_id}", response_model=user_schema.UserResponse) # R
def read_user_by_id(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a user using Id.
    """
    user_repo = UserRepositoryImpl(db)
    db_user = user_ops.get_user_by_id(user_repo = user_repo,  user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    return db_user


@router.post("/", response_model=user_schema.UserResponse, # C
             status_code=status.HTTP_201_CREATED)
def create_user(
    user: user_schema.UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    user_repo = UserRepositoryImpl(db)
    if current_user.role != "admin" and user.role == "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="You are not authorized to create admin users")
    db_user = user_ops.get_user_by_email(user_repo = user_repo,  email=user.email)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Email already registered")
    db_user = user_ops.get_user_by_phone(user_repo = user_repo,  phone=user.phone)
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                            detail="Phone already registered")
    return user_ops.create_user(user_repo = user_repo,  user=user)
@router.put("/{user_id}", response_model=user_schema.UserResponse)
def update_user(
    user_id: int,
    user_update: user_schema.UserUpdate,
    db: Session = Depends(get_db)
):
    user_repo = UserRepositoryImpl(db)
    # Check if user exists
    existing_user = user_ops.get_user_by_id(user_repo = user_repo,  user_id=user_id)
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    
    # Check email uniqueness if being updated
    if user_update.email and user_update.email != existing_user.email:
        db_user = user_ops.get_user_by_email(user_repo = user_repo,  email=user_update.email)
        if db_user and db_user.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered to another user"
            )
    
    # Check phone uniqueness if being updated
    if user_update.phone and user_update.phone != existing_user.phone:
        db_user = user_ops.get_user_by_phone(user_repo = user_repo,  phone=user_update.phone)
        if db_user and db_user.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered to another user"
            )
    
    # Update the user
    updated_user = user_ops.update_user(user_repo = user_repo,  user_id=user_id, user=user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )
    
    # Return the updated user object
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_200_OK) # D
def delete_user(user_id: int, 
                current_user: User = Depends(has_role('admin')),
                db: Session = Depends(get_db)):
    user_repo = UserRepositoryImpl(db)
    if current_user.user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin users cannot delete their own account."
        )
    if not user_ops.delete_user(user_repo = user_repo,  user_id=user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return {"message":f"user with user_id {user_id} was successully deleted"}

