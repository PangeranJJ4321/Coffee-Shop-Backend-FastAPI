"""
Schemas for payment processing
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.order import StatusType

class PaymentRequest(BaseModel):
    order_id: UUID
    payment_method: str = Field(..., description="Payment method (e.g., 'bank_transfer', 'credit_card', 'gopay')")

class PayForOthersRequest(BaseModel):
    """Request to pay for someone else's order"""
    order_id: UUID = Field(..., description="Order ID to pay for")
    payment_method: str = Field(..., description="Payment method (e.g., 'bank_transfer', 'credit_card', 'gopay')")
    note: Optional[str] = Field(None, description="Optional note for the payment")

class PaymentResponse(BaseModel):
    order_id: UUID
    transaction_id: str
    gross_amount: int
    payment_type: str
    transaction_time: datetime
    expiry_time: datetime
    payment_url: str
    token: Optional[str] = None

class PayForOthersResponse(BaseModel):
    """Response for pay for others payment"""
    order_id: UUID
    transaction_id: str
    gross_amount: int
    payment_type: str
    transaction_time: datetime
    expiry_time: datetime
    payment_url: str
    token: Optional[str] = None
    original_order_user_name: str
    original_order_user_email: str
    paid_by_user_name: str
    note: Optional[str] = None

class PaymentStatusResponse(BaseModel):
    order_id: UUID
    transaction_id: str
    status: StatusType
    payment_type: str
    transaction_time: datetime
    gross_amount: int
    payment_time: Optional[datetime] = None
    paid_by_user_id: Optional[UUID] = None
    paid_by_user_name: Optional[str] = None

class OrderPaymentInfoResponse(BaseModel):
    """Response for getting order payment information"""
    order_id: UUID
    order_number: str
    total_price: int
    status: str
    ordered_at: datetime
    user_name: str
    user_email: str
    is_paid: bool
    paid_by_user_id: Optional[UUID] = None
    paid_by_user_name: Optional[str] = None
    can_be_paid_by_others: bool