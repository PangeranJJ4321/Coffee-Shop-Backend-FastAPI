from datetime import datetime
from typing import List, Dict, Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, validator

from app.models.user import Role
from app.schemas.coffee_schema import CoffeeMenuPublicResponse

class UserBase(BaseModel):
    """Base user schema"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone_number: Optional[str] = None
    
    # @validator('phone_number')
    # def validate_phone(cls, v):
    #     if v and not v.startswith('+'):
    #         return f"{v}" # kedepannya mungkin kedepannya bisa di tambahin +62
    #     return v

class UserUpdate(UserBase):
    """User update schema"""
    password: Optional[str] = Field(None, min_length=8)
    
    # @validator('phone_number')
    # def validate_phone(cls, v):
    #     if v and not v.startswith('+'):
    #         return f"+{v}"
    #     return v

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8) 
    confirm_new_password: str = Field(..., min_length=8)

    @validator('confirm_new_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('New passwords do not match')
        return v

class UserResponse(BaseModel):
    """User response schema"""
    id: UUID
    name: str
    email: EmailStr
    phone_number: Optional[str] = None
    role: Role
    is_verified: Optional[bool]
    
    class Config:
        from_attributes = True

class UserProfile(UserResponse):
    favorites: List['CoffeeMenuPublicResponse'] = [] 
    bookings_count: int = 0
    orders_count: int = 0

    orders_created_count: int = 0
    orders_paid_for_others_count: int = 0
    orders_paid_by_others_count: int = 0
    total_spent_amount: int = 0
    average_order_value: float = 0.0 

    
    member_since: datetime 

    class Config:
        from_attributes = True

class UserRoleUpdate(BaseModel):
    role: Role