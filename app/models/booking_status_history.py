"""
Model for booking status history tracking
"""
from sqlalchemy import Column, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.models.base import BaseModel  
from app.models.booking import BookingStatus

class BookingStatusHistoryModel(BaseModel):
    __tablename__ = "booking_status_history"

    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    old_status = Column(Enum(BookingStatus), nullable=True)  # null for initial status
    new_status = Column(Enum(BookingStatus), nullable=False)
    changed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    booking = relationship("BookingModel", back_populates="status_history")
    changed_by_user = relationship("UserModel", foreign_keys=[changed_by_user_id])

    def __repr__(self):
        return f"<BookingStatusHistory {self.booking_id}: {self.old_status} -> {self.new_status}>"
