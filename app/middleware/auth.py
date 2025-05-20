from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.user import UserModel
from app.services.user_service import get_user_by_email
from app.utils.security import create_verification_token, decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> UserModel:
    """Get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = await get_user_by_email(db, email)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    
    return user

async def get_current_active_verified_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    """Get current active and verified user"""
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified"
        )
    return current_user

def generate_verification_token(email: str) -> str:
    """Generate verification token"""
    return create_verification_token(email)

def is_verification_token_valid(user: UserModel) -> bool:
    """Check if verification token is valid"""
    if not user.verification_token:
        return False
    
    if not user.verification_token_expires:
        return False
    
    return user.verification_token_expires > datetime.utcnow()