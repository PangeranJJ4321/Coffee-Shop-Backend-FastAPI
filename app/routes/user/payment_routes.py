"""
Routes for payment processing with Midtrans
"""
from typing import Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import UserModel
from app.schemas.payment_schema import (
    PaymentRequest,
    PaymentResponse,
    PaymentNotification
)
from app.services.payment_service import payment_service
from app.utils.security import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Create a payment token for an order (Midtrans integration)"""
    return payment_service.create_payment(db, payment_data, current_user.id)

@router.get("/{order_id}/status")
async def check_payment_status(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Check the payment status for an order"""
    status_response = payment_service.check_payment_status(db, order_id, current_user.id)
    if not status_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found for the specified order"
        )
    return status_response

@router.post("/notification", status_code=status.HTTP_200_OK)
async def handle_payment_notification(
    notification: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """Handle webhook notifications from Midtrans"""
    try:
        payment_service.process_notification(db, notification)
        return {"status": "OK"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing notification: {str(e)}"
        )