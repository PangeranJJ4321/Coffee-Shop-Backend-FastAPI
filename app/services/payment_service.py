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
    
    def create_