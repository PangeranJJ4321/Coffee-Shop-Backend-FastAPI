"""
Enhanced payment service for handling Midtrans integration with pay for others feature
"""
import uuid
import json
import hashlib
import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.order import OrderModel, OrderStatus, TransactionModel, StatusType
from app.models.order_status_history import OrderStatusHistoryModel
from app.models.user import UserModel
from app.models.notification import NotificationModel
from app.schemas.payment_schema import (
    PaymentRequest, 
    PaymentResponse, 
    PayForOthersRequest, 
    PayForOthersResponse
)


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
    
    def _process_midtrans_response_data(
        self, 
        order_id: uuid.UUID, 
        order_total_price: int, 
        payment_type: str, 
        midtrans_response: Dict[str, Any], 
        transaction_time: datetime, 
        expiry_time: datetime, 
        # Parameter opsional untuk PayForOthersResponse
        original_order_user_name: Optional[str] = None, 
        original_order_user_email: Optional[str] = None, 
        paid_by_user_name: Optional[str] = None, 
        note: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Helper function to extract relevant data from Midtrans response
        and format it for PaymentResponse or PayForOthersResponse.
        """
        payment_url = midtrans_response.get("redirect_url", "")
        token = midtrans_response.get("token", None)
        va_numbers = midtrans_response.get("va_numbers", None)
        actions = midtrans_response.get("actions", None) # Ini untuk GoPay (QR, deeplink)
        
        qr_code_url = None
        deeplink_url = None
        if actions:
            for action in actions:
                # Midtrans GoPay QR action name is typically "generate_qr_code"
                if action.get("name") == "generate-qr-code" and action.get("url"):
                    qr_code_url = action.get("url")
                    break
                # If you also need deeplink:
                elif action.get("name") == "deeplplink_redirect" and action.get("url"):
                    deeplink_url = action.get("url")
                    break

        response_data = {
            "order_id": order_id,
            "transaction_id": midtrans_response.get("transaction_id", midtrans_response.get("order_id")), # Fallback to order_id if transaction_id not present
            "gross_amount": order_total_price,
            "payment_type": payment_type,
            "transaction_time": transaction_time,
            "expiry_time": expiry_time,
            "payment_url": payment_url,
            "token": token,
            "va_numbers": va_numbers,
            "actions": actions, 
            "qr_code_url": qr_code_url, # Sertakan URL QR jika ditemukan
            "deeplink_url": deeplink_url
        }

        if original_order_user_name and original_order_user_email and paid_by_user_name:
            response_data.update({
                "original_order_user_name": original_order_user_name,
                "original_order_user_email": original_order_user_email,
                "paid_by_user_name": paid_by_user_name,
                "note": note
            })
        return response_data

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
        transaction_id_db = f"PFO-{uuid.uuid4().hex[:8].upper()}"

        # Set expiry time (24 hours from now)
        expiry_time = datetime.utcnow() + timedelta(hours=24)
        transaction_time = datetime.utcnow() # Define transaction_time here

        # Create payment payload for Midtrans
        payload = {
            "transaction_details": {
                "order_id": f"{order.order_id}-PFO-{payer_user_id.hex[:8]}",
                "gross_amount": order.total_price
            },
            "customer_details": {
                "first_name": payer_user.name,
                "email": payer_user.email,
                "phone": payer_user.phone_number
            },
            "expiry": {
                "start_time": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S +0700"),
                "unit": "minutes",
                "duration": 1440
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
                "bank": "bca"
            }
        else:
            endpoint = f"{self.api_base_url}/v2/charge"
            payload["payment_type"] = payment_type

        # Make request to Midtrans API
        headers = self._get_auth_header()
        headers["Content-Type"] = "application/json"

        midtrans_response = {}
        response_data = {}

        try:
            response = requests.post(
                endpoint,
                headers=headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
            midtrans_response = response.json()

            logger.info(f"Pay for others payment request created: {midtrans_response}")

            # Pindahkan panggilan _process_midtrans_response_data ke sini
            response_data = self._process_midtrans_response_data(
                order_id=order.id,
                order_total_price=order.total_price,
                payment_type=payment_type,
                midtrans_response=midtrans_response,
                transaction_time=transaction_time, # Gunakan variabel yang sudah didefinisikan
                expiry_time=expiry_time, # Gunakan variabel yang sudah didefinisikan
                original_order_user_name=order.user.name,
                original_order_user_email=order.user.email,
                paid_by_user_name=payer_user.name,
                note=payment_data.note
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Payment gateway error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Payment gateway error: {str(e)}"
            )

        # Save transaction to database
        transaction = TransactionModel(
            transaction_id=midtrans_response.get("transaction_id", transaction_id_db),
            order_id=order.id,
            gross_amount=order.total_price,
            status=StatusType.PENDING,
            transaction_time=transaction_time, # Gunakan variabel yang sudah didefinisikan
            expiry_time=expiry_time, # Gunakan variabel yang sudah didefinisikan
            payment_type=payment_type,
            qr_code_url=response_data.get("qr_code_url"), # Sekarang response_data sudah terisi
            deeplink_url=response_data.get("deeplink_url") # Sekarang response_data sudah terisi
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

        # Prepare response using the helper - ini sudah dipindahkan ke atas
        return PayForOthersResponse(**response_data)


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

        # Generate transaction ID for our internal DB
        transaction_id_db = f"TRX-{uuid.uuid4().hex[:8].upper()}"

        # Set expiry time (24 hours from now)
        expiry_time = datetime.utcnow() + timedelta(hours=24)
        transaction_time = datetime.utcnow() # Define transaction_time here

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
                "duration": 1440
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
                "bank": "bca"
            }
        else:
            endpoint = f"{self.api_base_url}/v2/charge"
            payload["payment_type"] = payment_type

        # Make request to Midtrans API
        headers = self._get_auth_header()
        headers["Content-Type"] = "application/json"

        midtrans_response = {}
        response_data = {}

        try:
            response = requests.post(
                endpoint,
                headers=headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
            midtrans_response = response.json()

            logger.info(f"Payment request created: {midtrans_response}")

            # Pindahkan panggilan _process_midtrans_response_data ke sini
            response_data = self._process_midtrans_response_data(
                order_id=order.id,
                order_total_price=order.total_price,
                payment_type=payment_type,
                midtrans_response=midtrans_response,
                transaction_time=transaction_time, # Gunakan variabel yang sudah didefinisikan
                expiry_time=expiry_time # Gunakan variabel yang sudah didefinisikan
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Payment gateway error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Payment gateway error: {str(e)}"
            )

        # Save transaction to database
        transaction = TransactionModel(
            transaction_id=midtrans_response.get("transaction_id", transaction_id_db),
            order_id=order.id,
            gross_amount=order.total_price,
            status=StatusType.PENDING,
            transaction_time=transaction_time, # Gunakan variabel yang sudah didefinisikan
            expiry_time=expiry_time, # Gunakan variabel yang sudah didefinisikan
            payment_type=payment_type ,
            qr_code_url=response_data.get("qr_code_url"), # Sekarang response_data sudah terisi
            deeplink_url=response_data.get("deeplink_url") # Sekarang response_data sudah terisi
        )
        db.add(transaction)

        # Update order status to PROCESSING and mark as self-paid
        order.status = OrderStatus.PROCESSING
        order.paid_by_user_id = user_id

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

        # Prepare response using the helper - ini sudah dipindahkan ke atas
        return PaymentResponse(**response_data)
    
    def check_payment_status(self, db: Session, order_id: uuid.UUID, user_id: uuid.UUID):
        """Check the status of a payment for an order and update history"""
        order = db.query(OrderModel).filter(
            OrderModel.id == order_id
        ).filter(
            (OrderModel.user_id == user_id) | (OrderModel.paid_by_user_id == user_id)
        ).first()

        if not order:
            return None

        transaction = db.query(TransactionModel).filter(
            TransactionModel.order_id == order.id
        ).order_by(TransactionModel.created_at.desc()).first()

        if not transaction:
            return None

        paid_by_user = None
        if order.paid_by_user_id:
            paid_by_user = db.query(UserModel).filter(
                UserModel.id == order.paid_by_user_id
            ).first()

        old_order_status = order.status # Capture old status before change

        if transaction.status == StatusType.PENDING:
            try:
                check_order_id = order.order_id
                if order.paid_by_user_id and order.paid_by_user_id != order.user_id:
                    check_order_id = f"{order.order_id}-PFO-{order.paid_by_user_id.hex[:8]}"

                endpoint = f"{self.api_base_url}/v2/{check_order_id}/status"
                headers = self._get_auth_header()

                response = requests.get(endpoint, headers=headers)
                response.raise_for_status()

                payment_data = response.json()
                logger.info(f"Payment status check: {payment_data}")

                if payment_data.get("transaction_status") == "settlement":
                    transaction.status = StatusType.SUCCESS
                    transaction.payment_time = datetime.now()
                    order.status = OrderStatus.CONFIRMED # Status baru: CONFIRMED
                    order.paid_at = datetime.utcnow()

                    # Create notifications for successful payment
                    if order.paid_by_user_id != order.user_id:
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
                        notification = NotificationModel(
                            type="payment_success",
                            message=f"Payment for order {order.order_id} has been completed successfully.",
                            is_read=False,
                            user_id=order.user_id
                        )
                        db.add(notification)

                elif payment_data.get("transaction_status") in ["expire", "cancel", "deny"]:
                    transaction.status = StatusType.FAILED
                    order.status = OrderStatus.CANCELLED # Status baru: CANCELLED
                    user_who_was_paying_id = order.paid_by_user_id
                    order.paid_by_user_id = None

                    # Create notifications for failed payment
                    if user_who_was_paying_id and user_who_was_paying_id != order.user_id:
                        notification_original = NotificationModel(
                            type="payment_failed",
                            message=f"Payment for your order {order.order_id} has failed or been cancelled. The order is now available for payment again.",
                            is_read=False,
                            user_id=order.user_id
                        )
                        db.add(notification_original)

                        notification_payer = NotificationModel(
                            type="payment_failed",
                            message=f"Payment for order {order.order_id} (for {order.user.name}) has failed or been cancelled.",
                            is_read=False,
                            user_id=user_who_was_paying_id
                        )
                        db.add(notification_payer)
                    else:
                        notification = NotificationModel(
                            type="payment_failed",
                            message=f"Payment for order {order.order_id} has failed or been cancelled.",
                            is_read=False,
                            user_id=order.user_id
                        )
                        db.add(notification)

                # --- ADD HISTORY RECORD FOR THIS STATUS CHANGE ---
                if old_order_status != order.status:
                    status_history_entry = OrderStatusHistoryModel(
                        order_id=order.id,
                        old_status=old_order_status,
                        new_status=order.status,
                        changed_by_user_id=user_id, # User who initiated check (or system)
                        notes=f"Status updated via payment check. Midtrans: {payment_data.get('transaction_status')}",
                        changed_at=datetime.utcnow()
                    )
                    db.add(status_history_entry)
                # --- END ADD HISTORY ---

                db.commit()
                db.refresh(transaction)
                db.refresh(order) # Refresh order to ensure history is loaded

            except requests.exceptions.RequestException as e:
                logger.error(f"Error checking payment status: {str(e)}")
                db.rollback()
                pass
            except Exception as e:
                logger.error(f"Error processing payment status update for order {order_id}: {str(e)}")
                db.rollback()
                pass

        return {
            "order_id": order.id,
            "transaction_id": transaction.transaction_id,
            "status": transaction.status,
            "payment_type": transaction.payment_type,
            "transaction_time": transaction.transaction_time,
            "gross_amount": transaction.gross_amount,
            "payment_time": transaction.payment_time,
            "paid_by_user_id": order.paid_by_user_id,
            "paid_by_user_name": paid_by_user.name if paid_by_user else None,
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
        Enhanced to handle pay-for-others transactions and update history
        """
        try:
            logger.info(f"Received payment notification: {notification}")

            if not settings.MIDTRANS_SANDBOX:
                is_valid_signature = self._verify_notification_signature(notification)
                if not is_valid_signature:
                    logger.warning("Invalid notification signature received")
                    raise ValueError("Invalid signature")

            order_id = notification.get("order_id")
            if not order_id:
                raise ValueError("Missing order_id in notification")

            original_order_id = order_id
            is_pay_for_others = "-PFO-" in order_id
            if is_pay_for_others:
                original_order_id = order_id.split("-PFO-")[0]

            order = db.query(OrderModel).filter(
                OrderModel.order_id == original_order_id
            ).first()

            if not order:
                logger.error(f"Order with ID {original_order_id} not found")
                raise ValueError(f"Order with ID {original_order_id} not found")

            transaction = db.query(TransactionModel).filter(
                TransactionModel.order_id == order.id
            ).order_by(TransactionModel.created_at.desc()).first()

            if not transaction:
                logger.error(f"No transaction found for order {original_order_id}")
                raise ValueError(f"No transaction found for order {original_order_id}")

            transaction_status = notification.get("transaction_status")
            logger.info(f"Processing transaction status: {transaction_status} for order {original_order_id}")

            payer_user = None
            if order.paid_by_user_id:
                payer_user = db.query(UserModel).filter(
                    UserModel.id == order.paid_by_user_id
                ).first()

            old_order_status = order.status # Capture old status before change

            if transaction_status in ["settlement", "capture"]:
                transaction.status = StatusType.SUCCESS
                transaction.payment_time = datetime.now()
                order.status = OrderStatus.CONFIRMED # Set to CONFIRMED
                order.paid_at = datetime.utcnow()

                # Create notifications
                if is_pay_for_others and payer_user and order.paid_by_user_id != order.user_id:
                    user_notification_original = NotificationModel(
                        type="payment_success",
                        message=f"Your order {order.order_id} has been paid successfully by {payer_user.name}. Thank you!",
                        is_read=False,
                        user_id=order.user_id
                    )
                    db.add(user_notification_original)

                    user_notification_payer = NotificationModel(
                        type="payment_success",
                        message=f"Payment for order {order.order_id} (for {order.user.name}) has been completed successfully. Thank you for your kindness!",
                        is_read=False,
                        user_id=order.paid_by_user_id
                    )
                    db.add(user_notification_payer)
                else:
                    user_notification = NotificationModel(
                        type="payment_success",
                        message=f"Your payment for order {order.order_id} has been completed successfully.",
                        is_read=False,
                        user_id=order.user_id
                    )
                    db.add(user_notification)
                logger.info(f"Payment successful for order {original_order_id}")

            elif transaction_status == "pending":
                logger.info(f"Payment pending for order {original_order_id}")
                # No change to order.status here as it should be PROCESSING from create_payment

            elif transaction_status in ["expire", "cancel", "deny"]:
                transaction.status = StatusType.FAILED
                order.status = OrderStatus.CANCELLED # Set to CANCELLED

                paid_by_user_id = order.paid_by_user_id
                order.paid_by_user_id = None

                # Create notifications
                if is_pay_for_others and payer_user and paid_by_user_id != order.user_id:
                    user_notification_original = NotificationModel(
                        type="payment_failed",
                        message=f"Payment for your order {order.order_id} has failed or been cancelled. The order is now available for payment again.",
                        is_read=False,
                        user_id=order.user_id
                    )
                    db.add(user_notification_original)

                    user_notification_payer = NotificationModel(
                        type="payment_failed",
                        message=f"Payment for order {order.order_id} (for {order.user.name}) has failed or been cancelled.",
                        is_read=False,
                        user_id=paid_by_user_id
                    )
                    db.add(user_notification_payer)
                else:
                    user_notification = NotificationModel(
                        type="payment_failed",
                        message=f"Your payment for order {order.order_id} has failed or been cancelled.",
                        is_read=False,
                        user_id=order.user_id
                    )
                    db.add(user_notification)
                logger.info(f"Payment failed for order {original_order_id}: {transaction_status}")

            # --- ADD HISTORY RECORD FOR THIS STATUS CHANGE ---
            if old_order_status != order.status:
                status_history_entry = OrderStatusHistoryModel(
                    order_id=order.id,
                    old_status=old_order_status,
                    new_status=order.status,
                    changed_by_user_id=None, # Changed by system (webhook)
                    notes=f"Status updated via Midtrans webhook: {transaction_status}.",
                    changed_at=datetime.utcnow()
                )
                db.add(status_history_entry)
            # --- END ADD HISTORY ---

            # Save additional payment details if available
            payment_details = {}
            payment_type = notification.get("payment_type")
            if payment_type:
                payment_details["payment_type"] = payment_type

                if payment_type == "bank_transfer":
                    if "va_numbers" in notification:
                        payment_details["va_numbers"] = notification["va_numbers"]
                elif payment_type == "credit_card":
                    if "masked_card" in notification:
                        payment_details["masked_card"] = notification["masked_card"]
                elif payment_type == "gopay":
                    if "actions" in notification:
                        payment_details["actions"] = notification["actions"]
                        for action in notification["actions"]:
                            if action.get("name") == "generate_qr_code" and action.get("url"):
                                payment_details["qr_code_url"] = action.get("url")
                                break

            if is_pay_for_others:
                payment_details["is_pay_for_others"] = True
                if payer_user:
                    payment_details["paid_by_user_name"] = payer_user.name
                    payment_details["paid_by_user_email"] = payer_user.email

            if payment_details:
                existing_note = order.payment_note or ""
                payment_details_json = json.dumps(payment_details)
                order.payment_note = f"{existing_note}\nPayment Details: {payment_details_json}" if existing_note else f"Payment Details: {payment_details_json}"

            db.commit()
            db.refresh(order)
            db.refresh(transaction)

            logger.info(f"Successfully processed notification for order {original_order_id}")
            return True

        except Exception as e:
            logger.error(f"Error processing payment notification: {str(e)}")
            raise
    def get_transaction_details(self, db: Session, order_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        transaction = db.query(TransactionModel).filter(
            TransactionModel.order_id == order_id,
        ).order_by(TransactionModel.created_at.desc()).first()

        if not transaction:
            return None

        order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
        if not order or (order.user_id != user_id and order.paid_by_user_id != user_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this transaction.")

        # Return a dictionary with all necessary details
        return {
            "id": transaction.id,
            "transaction_id": transaction.transaction_id,
            "gross_amount": transaction.gross_amount,
            "status": transaction.status.value, 
            "payment_time": transaction.payment_time.isoformat() if transaction.payment_time else None,
            "expiry_time": transaction.expiry_time.isoformat() if transaction.expiry_time else None,
            "transaction_time": transaction.transaction_time.isoformat() if transaction.transaction_time else None,
            "payment_type": transaction.payment_type,
            "qr_code_url": transaction.qr_code_url,
            "deeplink_url": transaction.deeplink_url,
            "order_id": str(order.id),
            "order_number": order.order_id,
            "order_total_price": order.total_price,
            "user_name": order.user.name,
            "user_email": order.user.email,
            "paid_by_user_id": str(order.paid_by_user_id) if order.paid_by_user_id else None,
            "paid_by_user_name": order.paid_by_user.name if order.paid_by_user else None,
        }
        
# Create singleton instance
payment_service = PaymentService()
