# Updated with pay for others endpoints

"""
Routes for payment processing with Midtrans, including pay for others feature
"""
from typing import Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response, Body
from sqlalchemy.orm import Session
import logging

from app.core.database import get_db
from app.models.user import UserModel
from app.schemas.payment_schema import (
    PaymentRequest,
    PaymentResponse,
    PaymentStatusResponse,
    PayForOthersRequest,
    PayForOthersResponse,
    OrderPaymentInfoResponse
)
from app.services.payment_service import payment_service
from app.utils.security import get_current_user

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.post("/create", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Create a payment token for an order (Midtrans integration)"""
    try:
        return payment_service.create_payment(db, payment_data, current_user.id)
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error creating payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating payment: {str(e)}"
        )

@router.get("/order/{order_id}/info", response_model=OrderPaymentInfoResponse)
async def get_order_payment_info(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get order information for payment (used when someone wants to pay for others)"""
    try:
        order_info = payment_service.get_order_payment_info(db, order_id)
        if not order_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        return order_info
    except HTTPException as e:
        raise
    except Exception as e:
        logger.error(f"Error getting order payment info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting order payment info: {str(e)}"
        )

@router.post("/pay-for-others", response_model=PayForOthersResponse)
async def pay_for_others(
    payment_data: PayForOthersRequest,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Pay for someone else's order"""
    try:
        return payment_service.pay_for_others(db, payment_data, current_user.id)
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error creating pay for others payment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating pay for others payment: {str(e)}"
        )

@router.get("/{order_id}/status", response_model=PaymentStatusResponse)
async def check_payment_status(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Check the payment status for an order"""
    try:
        status_response = payment_service.check_payment_status(db, order_id, current_user.id)
        if not status_response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found for the specified order"
            )
        return status_response
    except HTTPException as e:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error checking payment status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking payment status: {str(e)}"
        )

@router.post("/notification", status_code=status.HTTP_200_OK)
async def handle_payment_notification(
    notification: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Handle webhook notifications from Midtrans
    
    This endpoint receives payment status updates from Midtrans.
    It should be configured in the Midtrans dashboard as your notification URL.
    """
    try:
        logger.info(f"Received notification from Midtrans: {notification}")
        payment_service.process_notification(db, notification)
        return {"status": "OK"}
    except Exception as e:
        logger.error(f"Error processing payment notification: {str(e)}")
        # Still return a 200 OK to Midtrans to prevent retries for non-recoverable errors
        # but log the error for investigation
        return {
            "status": "ERROR",
            "message": str(e)
        }

# Optional additional endpoint for handling payment completion redirects
@router.get("/finished/{order_id}")
async def payment_finished(
    order_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle redirect after payment completion
    
    This endpoint should be configured as the 'finish' redirect URL in Midtrans.
    It allows users to return to your app after completing payment.
    """
    logger.info(f"Payment finished for order {order_id}")
    # You might want to redirect to an order confirmation page
    # This is just a simple response for now
    return {"message": "Payment process completed, thank you!"}

@router.get("/error/{order_id}")
async def payment_error(
    order_id: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle redirect after payment error
    
    This endpoint should be configured as the 'error' redirect URL in Midtrans.
    It allows users to return to your app after payment errors.
    """
    logger.info(f"Payment error for order {order_id}")
    # You might want to redirect to a payment retry page
    # This is just a simple response for now
    return {"message": "There was an issue with your payment. Please try again."}