from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.src.application.use_cases import user_ops
from backend.src.domain.entities.library_entities.user import User
from backend.src.domain.exceptions.user_exceptions import UserNotFound
from backend.src.infrastructure.persistence.database import get_db
from backend.src.infrastructure.persistence.repository_impl.library_repos_impl.user_repository_impl import \
    UserRepositoryImpl
from backend.src.infrastructure.web.auth_provider import (get_current_user,
                                                          has_role)
from backend.src.presentation.schemas.library_schemas import user_schema

router = APIRouter(prefix="/users", tags=["Users"])



@router.get("/me", response_model=user_schema.UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Return the current user's simple information.
    """
    return current_user


@router.get("/", response_model=List[user_schema.UserResponse])  # R
def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(has_role("admin")),
    db: Session = Depends(get_db),
):
    """
    Retrieve all users, default to 0-100
    """
    user_repo = UserRepositoryImpl(db)
    user_use_case = user_ops.GetUserUseCase(user_repo=user_repo)
    users = user_use_case.get_users(current_user=current_user, skip=skip, limit=limit)
    return users


@router.get("", response_model=List[user_schema.UserResponse])  # R
def search_users(
    text_to_search: str,
    skip: Optional[int] = 0,
    limit: Optional[int] = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_role("admin")),
):
    """
    Retrieve all users with matching information, default to 0-100
    """

    user_repo = UserRepositoryImpl(db)
    user_use_case = user_ops.SearchUserUseCase(user_repo=user_repo)
    users = user_use_case.execute(current_user=current_user, text_to_search=text_to_search, skip=skip, limit=limit
    )
    return users


@router.post(
    "/",
    response_model=user_schema.UserResponse,  # C
    status_code=status.HTTP_201_CREATED,
)
def create_user(
    user: user_schema.UserCreate,
    db: Session = Depends(get_db),
):
    user_repo = UserRepositoryImpl(db)

    try:
        create_user_use_case = user_ops.CreateUserUseCase(user_repo=user_repo)
    except UserNotFound:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User creation failed due to existing user.",
        )
    return create_user_use_case.execute(user=User(**user.model_dump())
    )


@router.put("/{user_id}", response_model=user_schema.UserResponse)
def update_user(
    user_id: int, user_update: user_schema.UserUpdate, db: Session = Depends(get_db),
    current_user: User = Depends(has_role("admin"))
):
    user_repo = UserRepositoryImpl(db)
    update_user_use_case = user_ops.UpdateUserUseCase(user_repo=user_repo)
    # Update the user
    try:
        updated_user = update_user_use_case.execute(
            current_user=current_user,
            user_id=user_id,
            data=user_update.model_dump(exclude_unset=True),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user",
        )

    # Return the updated user object
    return updated_user


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)  # D
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(has_role("admin"))
):
    user_repo = UserRepositoryImpl(db)
    delete_user_use_case = user_ops.DeleteUserUseCase(user_repo=user_repo)
    try:
        delete_user_use_case.execute(current_user=current_user, user_id=user_id)
    except UserNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return {"message": f"user with user_id {user_id} was successully deleted"}
