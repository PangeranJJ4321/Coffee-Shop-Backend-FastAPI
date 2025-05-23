"""
Booking and table models
"""
import enum
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class BookingStatus(enum.Enum):
    """Booking status enum"""
    NOCONFIRM = "NOCONFIRM"  # Initial state, waiting for confirmation
    CONFIRM = "CONFIRM"      # Confirmed by admin, waiting for payment
    SUCCESS = "SUCCESS"      # Payment completed, booking successful
    CANCELLED = "CANCELLED"  # Booking cancelled

class TableModel(BaseModel):
    """Table model for coffee shop tables"""
    __tablename__ = "tables"
    
    table_number = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    
    # Foreign keys
    coffee_shop_id = Column(UUID(as_uuid=True), ForeignKey("coffee_shops.id"), nullable=False)
    
    # Relationships
    coffee_shop = relationship("CoffeeShopModel", back_populates="tables")
    booking_tables = relationship("BookingTableModel", back_populates="table")
    
    def __repr__(self):
        return f"<Table {self.table_number}>"

class BookingModel(BaseModel):
    """Booking model for table reservations"""
    __tablename__ = "bookings"
    
    booking_id = Column(String, unique=True, nullable=False)
    table_count = Column(Integer, nullable=False)
    guest_count = Column(Integer, nullable=False)
    status = Column(Enum(BookingStatus), nullable=False, default=BookingStatus.NOCONFIRM)
    booking_date = Column(DateTime, nullable=False)
    booking_reminder_sent = Column(Boolean, default=False, nullable=False)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True)
    
    # Relationships
    user = relationship("UserModel", back_populates="bookings")
    order = relationship("OrderModel", back_populates="booking")
    booking_tables = relationship("BookingTableModel", back_populates="booking")
    status_history = relationship("BookingStatusHistoryModel", back_populates="booking")
    
    def __repr__(self):
        return f"<Booking {self.booking_id}>"

class BookingTableModel(BaseModel):
    """Booking table model to connect bookings with tables"""
    __tablename__ = "booking_tables"
    
    # Foreign keys
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id"), nullable=False)
    table_id = Column(UUID(as_uuid=True), ForeignKey("tables.id"), nullable=False)
    
    # Relationships
    booking = relationship("BookingModel", back_populates="booking_tables")
    table = relationship("TableModel", back_populates="booking_tables")
    
    def __repr__(self):
        return f"<BookingTable {self.id}>"