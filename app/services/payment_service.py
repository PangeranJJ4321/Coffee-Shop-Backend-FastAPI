"""
Enhanced payment service for handling Midtrans integration with improved notification handling
"""
import uuid
import json
import hashlib
import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.order import OrderModel, OrderStatus, TransactionModel, StatusType
from app.models.notification import NotificationModel
from app.schemas.payment_schema import PaymentRequest


# Set up logging
logger = logging.getLogger(__name__)


class PaymentService:
    def __init__(self):
        self.api_base_url = "https://api.sandbox.midtrans.com" if settings.MIDTRANS_SANDBOX else "https://api.midtrans.com"
        self.client_key = settings.MIDTRANS_CLIENT_KEY
        self.server_key = settings.MIDTRANS_SERVER_KEY
        
    def _get_auth_header(self):
        """Get authorization header for Midtrans API"""
        import base64
        auth_string = f"{self.server_key}:"
        auth_bytes = auth_string.encode("ascii")
        base64_bytes = base64.b64encode(auth_bytes)
        base64_auth = base64_bytes.decode("ascii")
        return {"Authorization": f"Basic {base64_auth}"}
    
    def create_payment(self, db: Session, payment_data: PaymentRequest, user_id: uuid.UUID):
        """Create a payment transaction for an order with Midtrans"""
        # Get the order
        order = db.query(OrderModel).filter(
            OrderModel.id == payment_data.order_id,
            OrderModel.user_id == user_id,
            OrderModel.status == OrderStatus.PENDING
        ).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found or not in pending state"
            )
        
        # Generate transaction ID
        transaction_id = f"TRX-{uuid.uuid4().hex[:8].upper()}"
        
        # Set expiry time (24 hours from now)
        expiry_time = datetime.utcnow() + timedelta(hours=24)
        
        # Create payment payload for Midtrans
        payload = {
            "transaction_details": {
                "order_id": order.order_id,
                "gross_amount": order.total_price
            },
            "customer_details": {
                "first_name": order.user.name,
                "email": order.user.email,
                "phone": order.user.phone_number
            },
            "expiry": {
                "start_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S +0700"),
                "unit": "minutes",
                "duration": 1440  # 24 hours in minutes
            },
            # This is important! Set your notification URL here as a fallback
            # in case the Midtrans dashboard configuration fails
            "callbacks": {
                "finish": f"{settings.BASE_URL}/payment/finished",
                "error": f"{settings.BASE_URL}/payment/error",
                "notification": f"{settings.BASE_URL}/payments/notification"
            }
        }
        
        # Handle different payment methods
        payment_type = payment_data.payment_method
        if payment_type == "credit_card":
            endpoint = f"{self.api_base_url}/v2/token"
            # Credit card specific settings would go here
        elif payment_type == "bank_transfer":
            endpoint = f"{self.api_base_url}/v2/charge"
            payload["payment_type"] = "bank_transfer"
            # Here we would specify bank details based on a selected bank
            payload["bank_transfer"] = {
                "bank": "bca"  # Default to BCA, could be parameterized
            }
        else:
            # For other payment types like GoPay, OVO, etc.
            endpoint = f"{self.api_base_url}/v2/charge"
            payload["payment_type"] = payment_type
        
        # Make request to Midtrans API
        headers = self._get_auth_header()
        headers["Content-Type"] = "application/json"
        
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
            payment_response = response.json()
            
            logger.info(f"Payment request created: {payment_response}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Payment gateway error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Payment gateway error: {str(e)}"
            )
        
        # Save transaction to database
        transaction = TransactionModel(
            transaction_id=transaction_id,
            order_id=order.id,
            gross_amount=order.total_price,
            status=StatusType.PENDING,
            transaction_time=datetime.utcnow(),
            expiry_time=expiry_time
        )
        db.add(transaction)
        
        # Update order status to PROCESSING
        order.status = OrderStatus.PROCESSING
        
        # Create a notification for the user
        notification = NotificationModel(
            type="payment_created",
            message=f"Payment for order {order.order_id} has been created. Please complete your payment.",
            is_read=False,
            user_id=user_id
        )
        db.add(notification)
        
        db.commit()
        db.refresh(transaction)
        
        # Prepare response
        return {
            "order_id": order.id,
            "transaction_id": transaction_id,
            "gross_amount": order.total_price,
            "payment_type": payment_type,
            "transaction_time": transaction.transaction_time,
            "expiry_time": transaction.expiry_time,
            "payment_url": payment_response.get("redirect_url", ""),
            "token": payment_response.get("token", None)
        }
    
    def check_payment_status(self, db: Session, order_id: uuid.UUID, user_id: uuid.UUID):
        """Check the status of a payment for an order"""
        # Get the order
        order = db.query(OrderModel).filter(
            OrderModel.id == order_id,
            OrderModel.user_id == user_id
        ).first()
        
        if not order:
            return None
        
        # Get the latest transaction for this order
        transaction = db.query(TransactionModel).filter(
            TransactionModel.order_id == order.id
        ).order_by(TransactionModel.created_at.desc()).first()
        
        if not transaction:
            return None
        
        # If the transaction is not in a final state, check with Midtrans
        if transaction.status == StatusType.PENDING:
            try:
                endpoint = f"{self.api_base_url}/v2/{order.order_id}/status"
                headers = self._get_auth_header()
                
                response = requests.get(endpoint, headers=headers)
                response.raise_for_status()
                
                payment_data = response.json()
                logger.info(f"Payment status check: {payment_data}")
                
                # Update transaction status based on Midtrans response
                if payment_data.get("transaction_status") == "settlement":
                    transaction.status = StatusType.SUCCESS
                    transaction.payment_time = datetime.now()
                    order.status = OrderStatus.COMPLETED
                    
                    # Create a notification for successful payment
                    notification = NotificationModel(
                        type="payment_success",
                        message=f"Payment for order {order.order_id} has been completed successfully.",
                        is_read=False,
                        user_id=order.user_id
                    )
                    db.add(notification)
                    
                elif payment_data.get("transaction_status") in ["expire", "cancel", "deny"]:
                    transaction.status = StatusType.FAILED
                    order.status = OrderStatus.CANCELLED
                    
                    # Create a notification for failed payment
                    notification = NotificationModel(
                        type="payment_failed",
                        message=f"Payment for order {order.order_id} has failed or been cancelled.",
                        is_read=False,
                        user_id=order.user_id
                    )
                    db.add(notification)
                
                db.commit()
                db.refresh(transaction)
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error checking payment status: {str(e)}")
                # In case of API error, return current status from DB
                pass
        
        # Return payment status information
        return {
            "order_id": order.id,
            "transaction_id": transaction.transaction_id,
            "status": transaction.status,
            "payment_type": "bank_transfer",  # This should ideally be stored in the transaction model
            "transaction_time": transaction.transaction_time,
            "gross_amount": transaction.gross_amount,
            "payment_time": transaction.payment_time
        }
    
    def _verify_notification_signature(self, notification: Dict[str, Any]) -> bool:
        """
        Verify Midtrans notification signature
        
        Signature is created from:
        order_id + status_code + gross_amount + server_key
        """
        order_id = notification.get("order_id", "")
        status_code = notification.get("status_code", "")
        gross_amount = notification.get("gross_amount", "")
        signature_key = notification.get("signature_key", "")
        
        # Create signature data
        signature_data = f"{order_id}{status_code}{gross_amount}{self.server_key}"
        
        # Generate SHA512 hash
        expected_signature = hashlib.sha512(signature_data.encode()).hexdigest()
        
        # Compare with received signature
        return signature_key == expected_signature
    
    def process_notification(self, db: Session, notification: Dict[str, Any]):
        """
        Process payment notification webhook from Midtrans
        
        Notification format from Midtrans:
        {
            "transaction_time": "2020-01-09 18:27:19",
            "transaction_status": "capture",
            "transaction_id": "57d5293c-e65f-4a29-95e4-5959c3fa335b",
            "status_message": "midtrans payment notification",
            "status_code": "200",
            "signature_key": "13f5f107cf9d676e34a2166c3330fd8cb89ab1a7593900577876ce24edfc8845c0543d13130682d17e411183d3ce7321fac0e14a1b48a714a599522b2e9f9f33",
            "payment_type": "credit_card",
            "order_id": "ORDER-101",
            "merchant_id": "G141532850",
            "gross_amount": "10000.00",
            "fraud_status": "accept",
            "currency": "IDR"
            ... additional payment specific fields ...
        }
        """
        try:
            # Log the incoming notification
            logger.info(f"Received payment notification: {notification}")
            
            # Verify the notification signature in production
            if not settings.MIDTRANS_SANDBOX:
                is_valid_signature = self._verify_notification_signature(notification)
                if not is_valid_signature:
                    logger.warning("Invalid notification signature received")
                    raise ValueError("Invalid signature")
            
            # Extract order ID from notification
            order_id = notification.get("order_id")
            if not order_id:
                raise ValueError("Missing order_id in notification")
            
            # Get the order from database
            order = db.query(OrderModel).filter(
                OrderModel.order_id == order_id
            ).first()
            
            if not order:
                logger.error(f"Order with ID {order_id} not found")
                raise ValueError(f"Order with ID {order_id} not found")
            
            # Get associated transaction
            transaction = db.query(TransactionModel).filter(
                TransactionModel.order_id == order.id
            ).order_by(TransactionModel.created_at.desc()).first()
            
            if not transaction:
                logger.error(f"No transaction found for order {order_id}")
                raise ValueError(f"No transaction found for order {order_id}")
            
            # Update transaction and order status based on notification
            transaction_status = notification.get("transaction_status")
            logger.info(f"Processing transaction status: {transaction_status} for order {order_id}")
            
            # Handle different transaction statuses
            if transaction_status in ["settlement", "capture"]:
                # Payment is successful and complete
                transaction.status = StatusType.SUCCESS
                transaction.payment_time = datetime.now()
                order.status = OrderStatus.COMPLETED
                
                # Create a notification for the user
                user_notification = NotificationModel(
                    type="payment_success",
                    message=f"Your payment for order {order.order_id} has been completed successfully.",
                    is_read=False,
                    user_id=order.user_id
                )
                db.add(user_notification)
                
                logger.info(f"Payment successful for order {order_id}")
                
            elif transaction_status == "pending":
                # Payment is created but not yet completed (e.g., waiting for bank transfer)
                # Status remains PENDING in our system
                logger.info(f"Payment pending for order {order_id}")
                
            elif transaction_status in ["expire", "cancel", "deny"]:
                # Payment failed or was cancelled
                transaction.status = StatusType.FAILED
                order.status = OrderStatus.CANCELLED
                
                # Create a notification for the user
                user_notification = NotificationModel(
                    type="payment_failed",
                    message=f"Your payment for order {order.order_id} has failed or been cancelled.",
                    is_read=False,
                    user_id=order.user_id
                )
                db.add(user_notification)
                
                logger.info(f"Payment failed for order {order_id}: {transaction_status}")
            
            # Save additional payment details if available
            payment_details = {}
            payment_type = notification.get("payment_type")
            if payment_type:
                payment_details["payment_type"] = payment_type
                
                # Extract payment type specific fields
                if payment_type == "bank_transfer":
                    if "va_numbers" in notification:
                        payment_details["va_numbers"] = notification["va_numbers"]
                elif payment_type == "credit_card":
                    if "masked_card" in notification:
                        payment_details["masked_card"] = notification["masked_card"]
                # Add more payment types as needed
            
            # Store payment note with details
            if payment_details:
                order.payment_note = json.dumps(payment_details)
            
            db.commit()
            logger.info(f"Successfully processed notification for order {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing payment notification: {str(e)}")
            raise

# Create singleton instance
payment_service = PaymentService()