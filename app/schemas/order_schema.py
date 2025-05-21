"""
Schemas for orders and order items
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, validator

from app.models.order import OrderStatus


class OrderItemVariantCreate(BaseModel):
    variant_id: UUID


class OrderItemCreate(BaseModel):
    coffee_id: UUID
    quantity: int = Field(..., gt=0)
    variants: List[OrderItemVariantCreate] = []
    
    @validator('quantity')
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v


class OrderCreate(BaseModel):
    order_items: List[OrderItemCreate]
    booking_id: Optional[UUID] = None


class OrderItemVariantResponse(BaseModel):
    id: UUID
    variant_id: UUID
    name: str
    variant_type: str
    additional_price: int

    class Config:
        orm_mode = True


class OrderItemResponse(BaseModel):
    id: UUID
    coffee_id: UUID
    coffee_name: str
    quantity: int
    subtotal: int
    variants: List[OrderItemVariantResponse] = []

    class Config:
        orm_mode = True


class OrderResponse(BaseModel):
    id: UUID
    order_id: str
    status: OrderStatus
    total_price: int
    ordered_at: datetime
    booking_id: Optional[UUID] = None

    class Config:
        orm_mode = True


class OrderWithItemsResponse(OrderResponse):
    order_items: List[OrderItemResponse]

    class Config:
        orm_mode = True


class OrderFilterParams(BaseModel):
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 10
    offset: int = 0