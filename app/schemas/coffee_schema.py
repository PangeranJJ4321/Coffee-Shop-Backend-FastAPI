"""
Pydantic schemas for coffee shop models
"""
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime

# ==================== Coffee Menu Schemas ====================

class CoffeeMenuBase(BaseModel):
    """Base schema for coffee menu items"""
    name: str
    price: int
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_available: bool = True

class CoffeeMenuCreate(CoffeeMenuBase):
    """Schema for creating a coffee menu item"""
    coffee_shop_id: UUID

class CoffeeMenuUpdate(BaseModel):
    """Schema for updating a coffee menu item"""
    name: Optional[str] = None
    price: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None
    coffee_shop_id: Optional[UUID] = None

class CoffeeMenuResponse(CoffeeMenuBase):
    """Schema for coffee menu item response"""
    id: UUID
    coffee_shop_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ==================== Variant Type Schemas ====================

class VariantTypeBase(BaseModel):
    """Base schema for variant types"""
    name: str
    description: Optional[str] = None
    is_required: bool = False

class VariantTypeCreate(VariantTypeBase):
    """Schema for creating a variant type"""
    pass

class VariantTypeUpdate(BaseModel):
    """Schema for updating a variant type"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_required: Optional[bool] = None

class VariantTypeResponse(VariantTypeBase):
    """Schema for variant type response"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ==================== Variant Schemas ====================

class VariantBase(BaseModel):
    """Base schema for variants"""
    name: str
    additional_price: int = 0
    is_available: bool = True

class VariantCreate(VariantBase):
    """Schema for creating a variant"""
    variant_type_id: UUID

class VariantUpdate(BaseModel):
    """Schema for updating a variant"""
    name: Optional[str] = None
    additional_price: Optional[int] = None
    is_available: Optional[bool] = None
    variant_type_id: Optional[UUID] = None

class VariantResponse(VariantBase):
    """Schema for variant response"""
    id: UUID
    variant_type_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ==================== Coffee Variant Schemas ====================

class CoffeeVariantBase(BaseModel):
    """Base schema for coffee variants"""
    is_default: bool = False

class CoffeeVariantCreate(CoffeeVariantBase):
    """Schema for creating a coffee variant"""
    coffee_id: UUID
    variant_id: UUID

class CoffeeVariantResponse(CoffeeVariantBase):
    """Schema for coffee variant response"""
    id: UUID
    coffee_id: UUID
    variant_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True