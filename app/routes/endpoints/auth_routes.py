from datetime import datetime, timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.config import settings
from app.core.database import get_db
from app.services.email import send_verification_email
from app.utils.security import create_access_token, create_refresh_token, create_verification_token, decode_token
from app.models.user import UserModel
from app.schemas.auth import LoginRequest, Token, RefreshTokenRequest, EmailVerificationRequest
from app.schemas.user import UserCreate, User
from app.services.user_service import (
    authenticate_user, create_user, update_user_last_login,
    get_user_by_verification_token, verify_user_email, get_user_by_email
)

router = APIRouter()


@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate, 
    db: Session = Depends(get_db)
) -> Any:
    """
    Register a new user
    """
    # Check if user exists
    user = await get_user_by_email(db, user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate verification token
    verification_token = create_verification_token(user_in.email)
    user_in.verification_token = verification_token
    
    # Create user
    user = await create_user(db, user_in)
    
    # Send verification email
    send_verification_email(user_in.email, verification_token)
    
    return user


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login
    """
    user = await authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    
    # Update last login
    await update_user_last_login(db, user)
    
    return {
        "access_token": create_access_token(user.email),
        "token_type": "bearer",
        "refresh_token": create_refresh_token(user.email)
    }


@router.post("/login/access-token", response_model=Token)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> Any:
    """
    OAuth2 compatible token login
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    
    # Update last login
    await update_user_last_login(db, user)
    
    return {
        "access_token": create_access_token(user.email),
        "token_type": "bearer",
        "refresh_token": create_refresh_token(user.email)
    }


@router.post("/refresh-token", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Refresh token
    """
    # Decode refresh token
    payload = decode_token(refresh_data.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user
    email = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = await get_user_by_email(db, email)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "access_token": create_access_token(user.email),
        "token_type": "bearer",
        "refresh_token": create_refresh_token(user.email)
    }


@router.post("/verify-email")
async def verify_email(
    verification_data: EmailVerificationRequest,
    db: Session = Depends(get_db)
) -> Any:
    """
    Verify email
    """
    user = await get_user_by_verification_token(db, verification_data.token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    if user.is_verified:
        return {"message": "Email already verified"}
    
    # Check if token is expired
    if user.verification_token_expires < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token expired"
        )
    
    # Verify user
    await verify_user_email(db, user)
    
    return {"message": "Email verified successfully"}


@router.post("/resend-verification")
async def resend_verification(
    email: str,
    db: Session = Depends(get_db)
) -> Any:
    """
    Resend verification email
    """
    user = await get_user_by_email(db, email)
    if not user:
        # Don't reveal that the user doesn't exist
        return {"message": "Verification email sent if account exists"}
    
    if user.is_verified:
        return {"message": "Email already verified"}
    
    # Generate new verification token
    verification_token = create_verification_token(email)
    
    # Update user
    user.verification_token = verification_token
    user.verification_token_expires = datetime.utcnow() + timedelta(hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS)
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Send verification email
    send_verification_email(email, verification_token)
    
    return {"message": "Verification email sent"}