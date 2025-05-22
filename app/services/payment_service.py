"""
Enhanced payment service for handling Midtrans integration with pay for others feature
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
from app.models.user import UserModel
from app.models.notification import NotificationModel
from app.schemas.payment_schema import PaymentRequest, PayForOthersRequest


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
    
    def get_order_payment_info(self, db: Session, order_id: uuid.UUID):
        """Get order information for payment processing"""
        order = db.query(OrderModel).filter(
            OrderModel.id == order_id
        ).first()
        
        if not order:
            return None
            
        # Check if order can be paid by others
        can_be_paid_by_others = (
            order.status == OrderStatus.PENDING and 
            order.paid_by_user_id is None
        )
        
        # Get paid by user info if exists
        paid_by_user = None
        if order.paid_by_user_id:
            paid_by_user = db.query(UserModel).filter(
                UserModel.id == order.paid_by_user_id
            ).first()
        
        return {
            "order_id": order.id,
            "order_number": order.order_id,
            "total_price": order.total_price,
            "status": order.status.value,
            "ordered_at": order.ordered_at,
            "user_name": order.user.name,
            "user_email": order.user.email,
            "is_paid": order.status in [OrderStatus.COMPLETED],
            "paid_by_user_id": paid_by_user.id if paid_by_user else None,
            "paid_by_user_name": paid_by_user.name if paid_by_user else None,
            "can_be_paid_by_others": can_be_paid_by_others
        }
    
    def pay_for_others(self, db: Session, payment_data: PayForOthersRequest, payer_user_id: uuid.UUID):
        """Create a payment transaction for someone else's order"""
        # Get the order
        order = db.query(OrderModel).filter(
            OrderModel.id == payment_data.order_id,
            OrderModel.status == OrderStatus.PENDING
        ).first()
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found or not in pending state"
            )
        
        # Check if order is already being paid by someone else
        if order.paid_by_user_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This order is already being paid by someone else"
            )
        
        # Get payer user info
        payer_user = db.query(UserModel).filter(UserModel.id == payer_user_id).first()
        if not payer_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payer user not found"
            )
        
        # Prevent users from paying for their own orders through this endpoint
        if order.user_id == payer_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot use pay-for-others endpoint for your own order. Use regular payment endpoint instead."
            )
        
        # Generate transaction ID with special prefix for pay-for-others
        transaction_id = f"PFO-{uuid.uuid4().hex[:8].upper()}"
        
        # Set expiry time (24 hours from now)
        expiry_time = datetime.utcnow() + timedelta(hours=24)
        
        # Create payment payload for Midtrans
        payload = {
            "transaction_details": {
                "order_id": f"{order.order_id}-PFO-{payer_user_id.hex[:8]}",  # Make unique for pay-for-others
                "gross_amount": order.total_price
            },
            "customer_details": {
                "first_name": payer_user.name,  # Payer's details
                "email": payer_user.email,
                "phone": payer_user.phone_number
            },
            "expiry": {
                "start_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S +0700"),
                "unit": "minutes",
                "duration": 1440  # 24 hours in minutes
            },
            "callbacks": {
                "finish": f"{settings.BASE_URL}/payment/finished",
                "error": f"{settings.BASE_URL}/payment/error",
                "notification": f"{settings.BASE_URL}/payments/notification"
            },
            # Add custom fields to identify this as pay-for-others
            "custom_field1": "pay_for_others",
            "custom_field2": str(order.id),
            "custom_field3": str(payer_user_id)
        }
        
        # Handle different payment methods
        payment_type = payment_data.payment_method
        if payment_type == "credit_card":
            endpoint = f"{self.api_base_url}/v2/token"
        elif payment_type == "bank_transfer":
            endpoint = f"{self.api_base_url}/v2/charge"
            payload["payment_type"] = "bank_transfer"
            payload["bank_transfer"] = {
                "bank": "bca"  # Default to BCA, could be parameterized
            }
        else:
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
            
            logger.info(f"Pay for others payment request created: {payment_response}")
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
        
        # Update order to mark who is paying and set status to PROCESSING
        order.paid_by_user_id = payer_user_id
        order.status = OrderStatus.PROCESSING
        if payment_data.note:
            order.payment_note = f"Paid by {payer_user.name}: {payment_data.note}"
        else:
            order.payment_note = f"Paid by {payer_user.name}"
        
        # Create notifications
        # Notification for the original order owner
        notification_original = NotificationModel(
            type="payment_by_others",
            message=f"{payer_user.name} is paying for your order {order.order_id}. Please wait for payment confirmation.",
            is_read=False,
            user_id=order.user_id
        )
        db.add(notification_original)
        
        # Notification for the payer
        notification_payer = NotificationModel(
            type="payment_created",
            message=f"Payment for order {order.order_id} (for {order.user.name}) has been created. Please complete your payment.",
            is_read=False,
            user_id=payer_user_id
        )
        db.add(notification_payer)
        
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
            "token": payment_response.get("token", None),
            "original_order_user_name": order.user.name,
            "original_order_user_email": order.user.email,
            "paid_by_user_name": payer_user.name,
            "note": payment_data.note
        }
    
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
        
        # Check if someone else is already paying for this order
        if order.paid_by_user_id is not None and order.paid_by_user_id != user_id:
            payer_user = db.query(UserModel).filter(UserModel.id == order.paid_by_user_id).first()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"This order is already being paid by {payer_user.name if payer_user else 'someone else'}"
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
        elif payment_type == "bank_transfer":
            endpoint = f"{self.api_base_url}/v2/charge"
            payload["payment_type"] = "bank_transfer"
            payload["bank_transfer"] = {
                "bank": "bca"  # Default to BCA, could be parameterized
            }
        else:
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
        
        # Update order status to PROCESSING and mark as self-paid
        order.status = OrderStatus.PROCESSING
        order.paid_by_user_id = user_id  # Mark that owner is paying for their own order
        
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
        # Get the order - allow checking if user is owner OR payer
        order = db.query(OrderModel).filter(
            OrderModel.id == order_id
        ).filter(
            (OrderModel.user_id == user_id) | (OrderModel.paid_by_user_id == user_id)
        ).first()
        
        if not order:
            return None
        
        # Get the latest transaction for this order
        transaction = db.query(TransactionModel).filter(
            TransactionModel.order_id == order.id
        ).order_by(TransactionModel.created_at.desc()).first()
        
        if not transaction:
            return None
        
        # Get paid by user info
        paid_by_user = None
        if order.paid_by_user_id:
            paid_by_user = db.query(UserModel).filter(
                UserModel.id == order.paid_by_user_id
            ).first()
        
        # If the transaction is not in a final state, check with Midtrans
        if transaction.status == StatusType.PENDING:
            try:
                # For pay-for-others transactions, we need to use the modified order_id
                check_order_id = order.order_id
                if order.paid_by_user_id and order.paid_by_user_id != order.user_id:
                    check_order_id = f"{order.order_id}-PFO-{order.paid_by_user_id.hex[:8]}"
                
                endpoint = f"{self.api_base_url}/v2/{check_order_id}/status"
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
                    
                    # Create notifications for successful payment
                    if order.paid_by_user_id != order.user_id:
                        # Pay for others scenario - notify both users
                        notification_original = NotificationModel(
                            type="payment_success",
                            message=f"Your order {order.order_id} has been paid successfully by {paid_by_user.name if paid_by_user else 'someone'}.",
                            is_read=False,
                            user_id=order.user_id
                        )
                        db.add(notification_original)
                        
                        notification_payer = NotificationModel(
                            type="payment_success",
                            message=f"Payment for order {order.order_id} (for {order.user.name}) has been completed successfully.",
                            is_read=False,
                            user_id=order.paid_by_user_id
                        )
                        db.add(notification_payer)
                    else:
                        # Regular payment
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
                    order.paid_by_user_id = None  # Reset the payer
                    
                    # Create notifications for failed payment
                    if order.paid_by_user_id != order.user_id:
                        # Pay for others scenario
                        notification_original = NotificationModel(
                            type="payment_failed",
                            message=f"Payment for your order {order.order_id} has failed or been cancelled.",
                            is_read=False,
                            user_id=order.user_id
                        )
                        db.add(notification_original)
                        
                        notification_payer = NotificationModel(
                            type="payment_failed",
                            message=f"Payment for order {order.order_id} (for {order.user.name}) has failed or been cancelled.",
                            is_read=False,
                            user_id=order.paid_by_user_id
                        )
                        db.add(notification_payer)
                    else:
                        # Regular payment
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
            "payment_time": transaction.payment_time,
            "paid_by_user_id": order.paid_by_user_id,
            "paid_by_user_name": paid_by_user.name if paid_by_user else None
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
        Enhanced to handle pay-for-others transactions
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
            
            # Handle pay-for-others order IDs (format: ORD-XXX-PFO-XXXX)
            original_order_id = order_id
            is_pay_for_others = "-PFO-" in order_id
            if is_pay_for_others:
                original_order_id = order_id.split("-PFO-")[0]
            
            # Get the order from database
            order = db.query(OrderModel).filter(
                OrderModel.order_id == original_order_id
            ).first()
            
            if not order:
                logger.error(f"Order with ID {original_order_id} not found")
                raise ValueError(f"Order with ID {original_order_id} not found")
            
            # Get associated transaction
            transaction = db.query(TransactionModel).filter(
                TransactionModel.order_id == order.id
            ).order_by(TransactionModel.created_at.desc()).first()
            
            if not transaction:
                logger.error(f"No transaction found for order {original_order_id}")
                raise ValueError(f"No transaction found for order {original_order_id}")
            
            # Update transaction and order status based on notification
            transaction_status = notification.get("transaction_status")
            logger.info(f"Processing transaction status: {transaction_status} for order {original_order_id}")
            
            # Get payer user info for notifications
            payer_user = None
            if order.paid_by_user_id:
                payer_user = db.query(UserModel).filter(
                    UserModel.id == order.paid_by_user_id
                ).first()
            
            # Handle different transaction statuses
            if transaction_status in ["settlement", "capture"]:
                # Payment is successful and complete
                transaction.status = StatusType.SUCCESS
                transaction.payment_time = datetime.now()
                order.status = OrderStatus.COMPLETED
                
                # Create notifications based on payment type
                if is_pay_for_others and payer_user and order.paid_by_user_id != order.user_id:
                    # Notify original order owner
                    user_notification_original = NotificationModel(
                        type="payment_success",
                        message=f"Your order {order.order_id} has been paid successfully by {payer_user.name}. Thank you!",
                        is_read=False,
                        user_id=order.user_id
                    )
                    db.add(user_notification_original)
                    
                    # Notify the payer
                    user_notification_payer = NotificationModel(
                        type="payment_success",
                        message=f"Payment for order {order.order_id} (for {order.user.name}) has been completed successfully. Thank you for your kindness!",
                        is_read=False,
                        user_id=order.paid_by_user_id
                    )
                    db.add(user_notification_payer)
                else:
                    # Regular payment notification
                    user_notification = NotificationModel(
                        type="payment_success",
                        message=f"Your payment for order {order.order_id} has been completed successfully.",
                        is_read=False,
                        user_id=order.user_id
                    )
                    db.add(user_notification)
                
                logger.info(f"Payment successful for order {original_order_id}")
                
            elif transaction_status == "pending":
                # Payment is created but not yet completed (e.g., waiting for bank transfer)
                # Status remains PENDING in our system
                logger.info(f"Payment pending for order {original_order_id}")
                
            elif transaction_status in ["expire", "cancel", "deny"]:
                # Payment failed or was cancelled
                transaction.status = StatusType.FAILED
                order.status = OrderStatus.CANCELLED
                
                # Reset the payer so order can be paid by someone else
                paid_by_user_id = order.paid_by_user_id
                order.paid_by_user_id = None
                
                # Create notifications based on payment type
                if is_pay_for_others and payer_user and paid_by_user_id != order.user_id:
                    # Notify original order owner
                    user_notification_original = NotificationModel(
                        type="payment_failed",
                        message=f"Payment for your order {order.order_id} has failed or been cancelled. The order is now available for payment again.",
                        is_read=False,
                        user_id=order.user_id
                    )
                    db.add(user_notification_original)
                    
                    # Notify the payer
                    user_notification_payer = NotificationModel(
                        type="payment_failed",
                        message=f"Payment for order {order.order_id} (for {order.user.name}) has failed or been cancelled.",
                        is_read=False,
                        user_id=paid_by_user_id
                    )
                    db.add(user_notification_payer)
                else:
                    # Regular payment notification
                    user_notification = NotificationModel(
                        type="payment_failed",
                        message=f"Your payment for order {order.order_id} has failed or been cancelled.",
                        is_read=False,
                        user_id=order.user_id
                    )
                    db.add(user_notification)
                
                logger.info(f"Payment failed for order {original_order_id}: {transaction_status}")
            
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
            
            # Add pay-for-others info to payment details
            if is_pay_for_others:
                payment_details["is_pay_for_others"] = True
                if payer_user:
                    payment_details["paid_by_user_name"] = payer_user.name
                    payment_details["paid_by_user_email"] = payer_user.email
            
            # Store payment note with details
            if payment_details:
                existing_note = order.payment_note or ""
                payment_details_json = json.dumps(payment_details)
                order.payment_note = f"{existing_note}\nPayment Details: {payment_details_json}" if existing_note else f"Payment Details: {payment_details_json}"
            
            db.commit()
            logger.info(f"Successfully processed notification for order {original_order_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing payment notification: {str(e)}")
            raise


# Create singleton instance
payment_service = PaymentService()