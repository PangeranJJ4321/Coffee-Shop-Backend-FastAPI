from datetime import datetime
from typing import List, Dict, Optional, Union
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, computed_field, validator

from app.models.user import Role
from app.schemas.coffee_schema import CoffeeMenuPublicResponse

class UserBase(BaseModel):
    """Base user schema"""
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    """User create schema"""
    password: str = Field(..., min_length=8)
    role: Role

    class Config:
        from_attributes = True



class UserUpdate(BaseModel):
    """User update schema"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8) 
    role: Optional[Role] = None
    status: Optional[bool] = None

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
    id: UUID
    name: str
    email: str
    phone_number: Optional[str] = None
    role: Role
    is_verified: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    total_orders_count: Optional[int] = 0
    total_spent_amount: Optional[int] = 0
    status: Optional[str] = None

    # ✅ Computed field untuk member_since
    @computed_field
    @property
    def member_since(self) -> datetime:
        """Member since adalah tanggal created_at"""
        return self.created_at
    
    # ✅ Computed field untuk login status
    @computed_field
    @property
    def has_logged_in(self) -> bool:
        """Apakah user pernah login"""
        return self.last_login is not None
    
    # ✅ Computed field untuk days since registration
    @computed_field
    @property
    def days_since_registration(self) -> int:
        """Berapa hari sejak registrasi"""
        from datetime import datetime
        return (datetime.utcnow() - self.created_at).days

    @validator('role', pre=True)
    def validate_role(cls, v):
        if hasattr(v, 'role'):
            return v.role
        elif isinstance(v, Role):
            return v
        elif isinstance(v, str):
            return Role(v)
        else:
            return Role.USER

    class Config:
        from_attributes = True
        use_enum_values = True

class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    per_page: int

class UserProfile(UserResponse):
    favorites: List['CoffeeMenuPublicResponse'] = [] 
    bookings_count: int = 0
    orders_count: int = 0

    orders_created_count: int = 0
    orders_paid_for_others_count: int = 0
    orders_paid_by_others_count: int = 0
    total_spent_amount: int = 0
    average_order_value: float = 0.0 
    
    # ✅ SOLUTION: Remove the conflicting member_since field
    # The computed field from UserResponse will be inherited automatically
    # If you need different logic for UserProfile, override the computed field instead:
    
    # @computed_field
    # @property
    # def member_since(self) -> datetime:
    #     """Custom member_since logic for UserProfile if needed"""
    #     return self.created_at

    class Config:
        from_attributes = True

class UserRoleUpdate(BaseModel):
    role: Role