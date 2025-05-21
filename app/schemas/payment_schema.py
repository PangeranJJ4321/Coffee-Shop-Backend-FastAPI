"""
Schemas for payment processing
"""
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

from app.models.order import StatusType


class PaymentRequest(BaseModel):
    order_id: UUID
    payment_method: str  # Examples: "credit_card", "bank_transfer", etc.


class PaymentResponse(BaseModel):
    order_id: UUID
    transaction_id: str
    gross_amount: int
    payment_type: str
    transaction_time: datetime
    expiry_time: Optional[datetime] = None
    payment_url: str  # For redirect-based payments like bank transfers
    token: Optional[str] = None  # For direct payments like credit cards


class PaymentStatusResponse(BaseModel):
    order_id: UUID
    transaction_id: str
    status: StatusType
    payment_type: str
    transaction_time: datetime
    gross_amount: int
    payment_time: Optional[datetime] = None


class PaymentNotification(BaseModel):
    transaction_id: str
    status_code: str
    gross_amount: str
    payment_type: str
    transaction_time: str
    transaction_status: str
    signature_key: str
    order_id: str
    fraud_status: Optional[str] = None
    settlement_time: Optional[str] = None
    status_message: Optional[str] = None
    payment_details: Optional[Dict[str, Any]] = None