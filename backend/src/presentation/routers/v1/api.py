from datetime import datetime, timedelta

import psutil
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.src.infrastructure.config.settings import settings
from backend.src.infrastructure.persistence.database import get_db
from backend.src.infrastructure.web.auth_provider import (
    ACCESS_TOKEN_EXPIRE_MINUTES, authenticate_user, create_access_token)
from backend.src.presentation.schemas.library_schemas import token_schema

SYSTEM_BOOT_TIME = datetime.fromtimestamp(psutil.boot_time())
APP_START_TIME = datetime.now()
APP_VERSION = settings.APP_VERSION

router = APIRouter()
@router.post("/token", response_model=token_schema.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    uptime_delta = datetime.now() - SYSTEM_BOOT_TIME
    total_seconds = int(uptime_delta.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    sys_uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

    app_uptime_delta = datetime.now() - APP_START_TIME
    total_seconds = int(app_uptime_delta.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    app_uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
        status_str = "healthy"
    except Exception as e:
        db_status = f"unavailable: {str(e)}"
        status_str = "degraded"
    return {
        "status": status_str,
        "database": db_status,
        "system_uptime": sys_uptime_str,
        "app_uptime": app_uptime_str,
        "total_token_validity": f"{ACCESS_TOKEN_EXPIRE_MINUTES} minutes",
        "version": APP_VERSION
    }
            