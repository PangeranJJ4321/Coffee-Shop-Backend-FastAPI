"""
Schemas for admin order management
"""
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.order import OrderStatus

class OrderStatusUpdate(BaseModel):
    status: OrderStatus
    notes: Optional[str] = Field(None, description="Optional notes for status change")

class BulkOrderStatusUpdate(BaseModel):
    order_ids: List[UUID] = Field(..., description="List of order IDs to update")
    status: OrderStatus
    notes: Optional[str] = Field(None, description="Optional notes for status change")

class OrderManagementResponse(BaseModel):
    id: UUID
    order_id: str
    status: OrderStatus
    total_price: int
    ordered_at: datetime
    user_id: UUID
    user_name: str
    user_email: str
    coffee_shop_id: UUID
    coffee_shop_name: str
    items_count: int
    items_summary: str
    payment_status: str # "Paid" or "Unpaid"
    paid_by_user_id: Optional[UUID] = None
    paid_by_user_name: Optional[str] = None
    booking_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime] = None 

    delivery_method: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_phone_number: Optional[str] = None
    delivery_address: Optional[str] = None
    order_notes: Optional[str] = None

    class Config:
        from_attributes = True
        use_enum_values = True

class OrderStatusHistoryResponse(BaseModel):
    id: UUID
    order_id: UUID
    old_status: Optional[OrderStatus] = None
    new_status: OrderStatus
    changed_by_user_id: Optional[UUID] = None
    changed_by_user_name: Optional[str] = None
    notes: Optional[str] = None
    changed_at: datetime

    class Config:
        from_attributes = True
        use_enum_values = True


class TodayOrdersSummary(BaseModel):
    date: datetime
    total_orders: int
    pending_orders: int
    processing_orders: int
    completed_orders: int
    cancelled_orders: int
    confirmed_orders: int = 0
    preparing_orders: int = 0
    ready_orders: int = 0
    delivered_orders: int = 0
    total_revenue: int
    status_breakdown: Dict[str, int]
    hourly_distribution: Dict[str, int]
    top_coffee_items: List[Dict[str, Any]]
    average_order_value: float
    peak_hour: str