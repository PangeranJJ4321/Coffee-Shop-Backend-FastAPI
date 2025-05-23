"""
Model for booking status history tracking
"""
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.core.database import Base
from app.models.booking import BookingStatus

class BookingStatusHistoryModel(Base):
    __tablename__ = "booking_status_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
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