from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.middleware.auth import get_current_active_verified_user
from app.models.user import UserModel
from app.schemas.user import User, UserUpdate
from app.services.user_service import update_user

router = APIRouter()


@router.get("/me", response_model=User)
async def read_user_me(
    current_user: UserModel = Depends(get_current_active_verified_user),
) -> Any:
    """
    Get current user
    """
    return current_user


@router.put("/me", response_model=User)
async def update_user_me(
    user_in: UserUpdate,
    current_user: UserModel = Depends(get_current_active_verified_user),
    db: Session = Depends(get_db),
) -> Any:
    """
    Update current user
    """
    user = await update_user(db, current_user, user_in)
    return user