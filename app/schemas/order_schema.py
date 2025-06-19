# app/schemas/order_schema.py - Updated with pay for others schemas -> lanjut service nya

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, computed_field

from app.models.order import OrderStatus

class OrderItemVariantCreate(BaseModel):
    variant_id: UUID

class OrderItemCreate(BaseModel):
    coffee_id: UUID
    quantity: int = Field(..., gt=0)
    variants: List[OrderItemVariantCreate] = []

class OrderDeliveryInfo(BaseModel):
    name: str
    phone_number: str
    address: Optional[str] = None
    email: Optional[str] = None
    notes: Optional[str] = None
    delivery_method: str # 'delivery' or 'pickup'

class OrderCreate(BaseModel):
    order_items: List[OrderItemCreate]
    booking_id: Optional[UUID] = None
    delivery_info: OrderDeliveryInfo

class OrderItemVariantResponse(BaseModel):
    id: UUID
    variant_id: UUID
    name: Optional[str] = None  # Enriched from variant
    variant_type: Optional[str] = None  # Enriched from variant type
    additional_price: Optional[int] = None  # Enriched from variant

    class Config:
        from_attributes = True

class CoffeeMenuResponseForOrderItem(BaseModel):
    id: UUID
    name: str
    price: int
    image_url: Optional[str] = None
    description: Optional[str] = None
    # Tambahkan atribut lain dari CoffeeMenuModel yang relevan jika dibutuhkan di frontend
    # Misalnya, coffee_shop_id, is_available, dll.

    class Config:
        from_attributes = True # Penting untuk memetakan dari SQLAlchemy CoffeeMenuModel

class VariantResponseForOrderItem(BaseModel):
    variant_id: UUID # Ini ID dari VariantModel
    name: str
    additional_price: int # Pastikan ini ada di VariantModel dan diambil
    variant_type: str # Pastikan ini ada di VariantModel dan diambil

class OrderItemResponse(BaseModel):
    id: UUID
    quantity: int
    subtotal: int
    coffee_id: UUID
    coffee_name: Optional[str] = None  # Enriched from coffee
    coffee: CoffeeMenuResponseForOrderItem
    variants: List[OrderItemVariantResponse] = []

    class Config:
        from_attributes = True

class OrderResponse(BaseModel):
    id: UUID
    order_id: str
    status: OrderStatus
    total_price: int
    ordered_at: datetime
    payment_note: Optional[str] = None
    
    user_id: UUID
    user_name: Optional[str] = None 
    user_email: Optional[str] = None 

    paid_by_user_id: Optional[UUID] = None
    paid_by_user_name: Optional[str] = None 

    payment_status: Optional[str] = None 

    created_at: datetime
    updated_at: datetime
    paid_at: Optional[datetime] = None
    
    # Atribut delivery yang di-flatten
    delivery_method: Optional[str] = None
    recipient_name: Optional[str] = None
    recipient_phone_number: Optional[str] = None
    delivery_address: Optional[str] = None
    order_notes: Optional[str] = None

    @computed_field
    @property
    def delivery_info(self) -> Optional[OrderDeliveryInfo]:
        if self.delivery_method:
            return OrderDeliveryInfo(
                name=self.recipient_name,
                phone_number=self.recipient_phone_number,
                email=self.user_email, 
                address=self.delivery_address,
                notes=self.order_notes,
                delivery_method=self.delivery_method
            )
        return None

    class Config:
        from_attributes = True
        use_enum_values = True

class OrderWithItemsResponse(OrderResponse):
    order_items: List[OrderItemResponse] = [] 

class PayableOrderResponse(BaseModel):
    """Response for orders that can be paid by others"""
    id: UUID
    order_id: str
    total_price: int
    ordered_at: datetime
    user_name: str
    user_email: str
    coffee_shop_name: Optional[str] = None
    items_count: int
    items_summary: str  # e.g., "2x Espresso, 1x Cappuccino"
    time_since_order: str  # e.g., "2 hours ago"

    class Config:
        from_attributes = True

class OrderFilterParams(BaseModel):
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(default=20, le=100)
    offset: int = Field(default=0, ge=0)