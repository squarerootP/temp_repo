from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.src.application.use_cases import user_ops
from backend.src.domain.entities.library_entities.user import User
from backend.src.domain.services.utils import verify_password
from backend.src.infrastructure.config.settings import settings
from backend.src.infrastructure.persistence.database import get_db
from backend.src.infrastructure.persistence.repository_impl.library_repos_impl.user_repository_impl import \
    UserRepositoryImpl
from backend.src.presentation.schemas.library_schemas import token_schema

SECRET_KEY = settings.SECRET_KEY
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/token")


def authenticate_user(db: Session, email: str, password: str):
    try:
        user_repo = UserRepositoryImpl(db)
        user_use_case = user_ops.GetUserUseCase(user_repo=user_repo)
        
        user = user_use_case.get_user_by_email(email=email)
        if not user:
            return False
        if not verify_password(password, user.hashed_password):
            return False
        return user
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_repo = UserRepositoryImpl(db)
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")  # type: ignore
        if email is None:
            raise credentials_exception
        token_data = token_schema.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    get_user_use_case = user_ops.GetUserUseCase(user_repo=user_repo)
    user = get_user_use_case.get_user_by_email(email=token_data.email) # type: ignore
    if user is None:
        raise credentials_exception
    return user


def has_role(required_role: str):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role {required_role} required",
            )
        return current_user

    return role_checker
