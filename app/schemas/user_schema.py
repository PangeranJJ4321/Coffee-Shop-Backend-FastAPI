from typing import List, Dict, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, validator

from app.models.user import Role

class UserBase(BaseModel):
    """Base user schema"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone_number: Optional[str] = None
    
    @validator('phone_number')
    def validate_phone(cls, v):
        if v and not v.startswith('+'):
            return f"+{v}"
        return v

class UserUpdate(BaseModel):
    """User update schema"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone_number: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    
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

class UserProfile(UserResponse):
    favorites: List[Dict] = []
    bookings_count: int = 0
    orders_count: int = 0
    
    class Config:
        from_attributes = True

class UserRoleUpdate(BaseModel):
    role: Role