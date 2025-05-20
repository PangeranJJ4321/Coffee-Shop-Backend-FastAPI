from typing import Optional
from pydantic import BaseModel, EmailStr, Field
import uuid
from datetime import datetime


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    name: str
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8)
    verification_token: Optional[str] = None


class UserUpdate(BaseModel):
    """User update schema"""
    name: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None


class UserInDBBase(UserBase):
    """User in DB base schema"""
    id: uuid.UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class User(UserInDBBase):
    """User schema"""
    pass


class UserInDB(UserInDBBase):
    """User in DB schema"""
    password_hash: str