from sqlalchemy import Column, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime

from app.models.base import BaseModel  
from app.models.order import OrderStatus

class OrderStatusHistoryModel(BaseModel):
    __tablename__ = "order_status_history"

    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    old_status = Column(Enum(OrderStatus), nullable=True)  # null for initial status
    new_status = Column(Enum(OrderStatus), nullable=False)
    changed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    order = relationship("OrderModel", back_populates="status_history")
    changed_by_user = relationship("UserModel", foreign_keys=[changed_by_user_id])

    def __repr__(self):
        return f"<OrderStatusHistory {self.order_id}: {self.old_status} -> {self.new_status}>"
