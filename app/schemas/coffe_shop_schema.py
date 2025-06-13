# app/schemas/coffee_shop_schema.py
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime # <-- Import datetime

# Schema untuk Coffee Shop
class CoffeeShopBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    address: str = Field(..., min_length=5, max_length=255)
    phone_number: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class CoffeeShopCreate(CoffeeShopBase):
    pass

class CoffeeShopUpdate(CoffeeShopBase):
    name: Optional[str] = None
    address: Optional[str] = None

class CoffeeShopResponse(CoffeeShopBase):
    id: UUID
    average_rating: Optional[float] = None
    total_ratings: int = 0
    created_at: datetime 
    updated_at: datetime 

    class Config:
        from_attributes = True 