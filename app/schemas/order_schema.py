# app/schemas/order_schema.py - Updated with pay for others schemas -> lanjut service nya

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.order import OrderStatus

class OrderItemVariantCreate(BaseModel):
    variant_id: UUID

class OrderItemCreate(BaseModel):
    coffee_id: UUID
    quantity: int = Field(..., gt=0)
    variants: List[OrderItemVariantCreate] = []

class OrderCreate(BaseModel):
    order_items: List[OrderItemCreate]
    booking_id: Optional[UUID] = None

class OrderItemVariantResponse(BaseModel):
    id: UUID
    variant_id: UUID
    name: Optional[str] = None  # Enriched from variant
    variant_type: Optional[str] = None  # Enriched from variant type
    additional_price: Optional[int] = None  # Enriched from variant

    class Config:
        from_attributes = True

class OrderItemResponse(BaseModel):
    id: UUID
    quantity: int
    subtotal: int
    coffee_id: UUID
    coffee_name: Optional[str] = None  # Enriched from coffee
    variants: List[OrderItemVariantResponse] = []

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: UUID
    order_id: str
    status: OrderStatus
    total_price: int
    ordered_at: datetime
    payment_note: Optional[str] = None
    user_id: UUID
    paid_by_user_id: Optional[UUID] = None
    paid_by_user_name: Optional[str] = None  # Enriched field
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class OrderWithItemsResponse(OrderResponse):
    order_items: List[OrderItemResponse] = []

class PayableOrderResponse(BaseModel):
    """Response for orders that can be paid by others"""
    id: UUID
    order_id: str
    total_price: int
    ordered_at: datetime
    user_name: str
    user_email: str
    coffee_shop_name: Optional[str] = None
    items_count: int
    items_summary: str  # e.g., "2x Espresso, 1x Cappuccino"
    time_since_order: str  # e.g., "2 hours ago"

    class Config:
        from_attributes = True

class OrderFilterParams(BaseModel):
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=20, le=100)
    offset: int = Field(default=0, ge=0)