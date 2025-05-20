from datetime import datetime, timedelta
from typing import Any, Optional
import secrets
import string
from passlib.context import CryptContext
from jose import jwt

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token related functions
def create_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT token"""
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def create_access_token(subject: Any) -> str:
    """Create access token"""
    return create_token(
        data={"sub": str(subject)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )

def create_refresh_token(subject: Any) -> str:
    """Create refresh token"""
    return create_token(
        data={"sub": str(subject)},
        expires_delta=timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    )

def create_verification_token(email: str) -> str:
    """Create verification token"""
    # Generate a random token
    chars = string.ascii_letters + string.digits
    token = ''.join(secrets.choice(chars) for _ in range(32))
    
    return token

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Get password hash"""
    return pwd_context.hash(password)

def decode_token(token: str) -> Optional[dict]:
    """Decode JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.JWTError:
        return None