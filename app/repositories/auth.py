from datetime import datetime, timedelta
import uuid
from typing import Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.user import get_user_by_email
from app.utils.security import get_password_hash, verify_password
from app.models.user import UserModel, RoleModel, Role
from app.schemas.user import UserCreate, UserUpdate

async def get_user_by_verification_token(db: Session, token: str) -> Optional[UserModel]:
    """Get user by verification token"""
    return db.query(UserModel).filter(UserModel.verification_token == token).first()

async def create_user(db: Session, user_in: UserCreate) -> UserModel:
    """Create new user"""
    # Get user role
    user_role = db.query(RoleModel).filter(RoleModel.role == Role.USER).first()
    if not user_role:
        # Create user role if it doesn't exist
        user_role = RoleModel(role=Role.USER)
        db.add(user_role)
        db.commit()
        db.refresh(user_role)
    
    # Create user
    verification_token = user_in.verification_token
    expires = datetime.utcnow() + timedelta(hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS)
    
    db_user = UserModel(
        name=user_in.name,
        email=user_in.email,
        phone_number=user_in.phone_number,
        password_hash=get_password_hash(user_in.password),
        is_active=True,
        is_verified=False,
        verification_token=verification_token,
        verification_token_expires=expires,
        role_id=user_role.id
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

async def verify_user_email(db: Session, user: UserModel) -> UserModel:
    """Verify user email"""
    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user

async def authenticate_user(db: Session, email: str, password: str) -> Optional[UserModel]:
    """Authenticate user"""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user

async def update_user_last_login(db: Session, user: UserModel) -> UserModel:
    """Update user last login time"""
    user.last_login = datetime.utcnow()
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user
