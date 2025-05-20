from datetime import datetime, timedelta
import uuid
from typing import Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.utils.security import get_password_hash, verify_password
from app.models.user import UserModel, RoleModel, Role
from app.schemas.user import UserCreate, UserUpdate


async def get_user_by_email(db: Session, email: str) -> Optional[UserModel]:
    """Get user by email"""
    return db.query(UserModel).filter(UserModel.email == email).first()

async def get_user_by_id(db: Session, user_id: uuid.UUID) -> Optional[UserModel]:
    """Get user by ID"""
    return db.query(UserModel).filter(UserModel.id == user_id).first()


async def update_user(db: Session, user: UserModel, user_in: UserUpdate) -> UserModel:
    """Update user"""
    if user_in.name is not None:
        user.name = user_in.name
    
    if user_in.phone_number is not None:
        user.phone_number = user_in.phone_number
    
    if user_in.password is not None:
        user.password_hash = get_password_hash(user_in.password)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user