"""
Order and payment models
"""
import enum
from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class OrderStatus(enum.Enum):
    """Order status enum"""
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED" 
    CANCELLED = "CANCELLED"

class StatusType(enum.Enum):
    """General status type for payments and transactions"""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class OrderModel(BaseModel):
    """Order model"""
    __tablename__ = "orders"
    
    order_id = Column(String, unique=True, nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    total_price = Column(Integer, nullable=False)
    ordered_at = Column(DateTime, nullable=False)
    payment_note = Column(Text, nullable=True)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    paid_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    user = relationship("UserModel", back_populates="orders", foreign_keys=[user_id])
    paid_by_user = relationship("UserModel", back_populates="paid_orders", foreign_keys=[paid_by_user_id])
    order_items = relationship("OrderItemModel", back_populates="order")
    transactions = relationship("TransactionModel", back_populates="order")
    booking = relationship("BookingModel", back_populates="order", uselist=False)
    status_history = relationship("OrderStatusHistoryModel", back_populates="order")

    def __repr__(self):
        return f"<Order {self.order_id}>"

class OrderItemModel(BaseModel):
    """Order item model"""
    __tablename__ = "order_items"
    
    quantity = Column(Integer, nullable=False)
    subtotal = Column(Integer, nullable=False)
    
    # Foreign keys
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    coffee_id = Column(UUID(as_uuid=True), ForeignKey("coffee_menu.id"), nullable=False)
    
    # Relationships
    order = relationship("OrderModel", back_populates="order_items")
    coffee = relationship("CoffeeMenuModel", back_populates="order_items")
    variants = relationship("OrderItemVariantModel", back_populates="order_item")
    
    def __repr__(self):
        return f"<OrderItem {self.id}>"

class OrderItemVariantModel(BaseModel):
    """Order item variant model"""
    __tablename__ = "order_item_variants"
    
    # Foreign keys
    order_item_id = Column(UUID(as_uuid=True), ForeignKey("order_items.id"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("variants.id"), nullable=False)
    
    # Relationships
    order_item = relationship("OrderItemModel", back_populates="variants")
    variant = relationship("VariantModel", back_populates="order_item_variants")
    
    def __repr__(self):
        return f"<OrderItemVariant {self.id}>"

class TransactionModel(BaseModel):
    """Transaction model for payment transactions"""
    __tablename__ = "transactions"
    
    transaction_id = Column(String, unique=True, nullable=False)
    gross_amount = Column(Integer, nullable=False)
    status = Column(Enum(StatusType), nullable=False, default=StatusType.PENDING)
    payment_time = Column(DateTime, nullable=True)
    expiry_time = Column(DateTime, nullable=True)
    transaction_time = Column(DateTime, nullable=False)
    
    # Foreign keys
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    
    # Relationships
    order = relationship("OrderModel", back_populates="transactions")
    payouts = relationship("PayoutModel", back_populates="transaction")
    
    def __repr__(self):
        return f"<Transaction {self.transaction_id}>"

class PayoutModel(BaseModel):
    """Payout model for handling merchant payouts"""
    __tablename__ = "payouts"
    
    amount = Column(Integer, nullable=False)
    bank_name = Column(String, nullable=False)
    account_number = Column(String, nullable=False)
    account_name = Column(String, nullable=False)
    reference_id = Column(String, unique=True, nullable=False)
    status = Column(Enum(StatusType), nullable=False, default=StatusType.PENDING)
    notes = Column(Text, nullable=True)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    transaction_id = Column(UUID(as_uuid=True), ForeignKey("transactions.id"), nullable=True)
    
    # Relationships
    user = relationship("UserModel", back_populates="payouts")
    transaction = relationship("TransactionModel", back_populates="payouts")
    
    def __repr__(self):
        return f"<Payout {self.reference_id}>"