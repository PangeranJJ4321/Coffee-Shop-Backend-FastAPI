"""
Payment service for handling Midtrans integration
"""
import uuid
import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.config import settings
from app.models.order import OrderModel, OrderStatus, TransactionModel, StatusType
from app.schemas.payment_schema import PaymentRequest


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
        except requests.exceptions.RequestException as e:
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
                
                # Update transaction status based on Midtrans response
                if payment_data.get("transaction_status") == "settlement":
                    transaction.status = StatusType.SUCCESS
                    transaction.payment_time = datetime.now()
                    order.status = OrderStatus.COMPLETED
                elif payment_data.get("transaction_status") in ["expire", "cancel", "deny"]:
                    transaction.status = StatusType.FAILED
                    order.status = OrderStatus.CANCELLED
                
                db.commit()
                db.refresh(transaction)
                
            except requests.exceptions.RequestException:
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
    
    def process_notification(self, db: Session, notification: Dict[str, Any]):
        """Process payment notification webhook from Midtrans"""
        # Verify the notification signature (production would need this)
        # This is simplified - real implementation would validate the signature
        
        # Extract order ID from notification
        order_id = notification.get("order_id")
        if not order_id:
            raise ValueError("Missing order_id in notification")
        
        # Get the order from database
        order = db.query(OrderModel).filter(
            OrderModel.order_id == order_id
        ).first()
        
        if not order:
            raise ValueError(f"Order with ID {order_id} not found")
        
        # Get associated transaction
        transaction = db.query(TransactionModel).filter(
            TransactionModel.order_id == order.id
        ).order_by(TransactionModel.created_at.desc()).first()
        
        if not transaction:
            raise ValueError(f"No transaction found for order {order_id}")
        
        # Update transaction and order status based on notification
        transaction_status = notification.get("transaction_status")
        
        if transaction_status == "settlement" or transaction_status == "capture":
            transaction.status = StatusType.SUCCESS
            transaction.payment_time = datetime.now()
            order.status = OrderStatus.COMPLETED
        elif transaction_status in ["expire", "cancel", "deny"]:
            transaction.status = StatusType.FAILED
            order.status = OrderStatus.CANCELLED
        
        db.commit()


# Create singleton instance
payment_service = PaymentService()