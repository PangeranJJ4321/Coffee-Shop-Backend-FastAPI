from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, validator

from app.models.user import Role

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserRegister(BaseModel):
    """User registration schema"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    phone_number: Optional[str] = None
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v
    
    @validator('phone_number')
    def validate_phone(cls, v):
        if v and not v.startswith('+'):
            return f"+{v}"
        return v

class UserResponse(BaseModel):
    """User response schema"""
    id: UUID
    name: str
    email: EmailStr
    phone_number: Optional[str] = None
    role: Role
    
    class Config:
        from_attributes = True

class EmailVerification(BaseModel):
    """Email verification schema"""
    token: str

class ResendVerification(BaseModel):
    """Resend verification email schema"""
    email: EmailStr

class PasswordReset(BaseModel):
    """Password reset schema"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Password reset confirmation schema"""
    token: str
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v