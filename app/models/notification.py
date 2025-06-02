from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class NotificationModel(BaseModel):
    """Notification model"""
    __tablename__ = "notifications"
    
    type = Column(String, nullable=False)  # e.g., "order_ready", "booking_confirmed"
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="notifications")
    
    def __repr__(self):
        return f"<Notification {self.id}>"

class UserFavoriteModel(BaseModel):
    """User favorite model for storing favorite coffee items"""
    __tablename__ = "user_favorites"
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    coffee_id = Column(UUID(as_uuid=True), ForeignKey("coffee_menu.id"), nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="favorites")
    coffee = relationship("CoffeeMenuModel", back_populates="favorites")
    
    def __repr__(self):
        return f"<UserFavorite {self.id}>"

class RatingModel(BaseModel):
    """Rating model for coffee ratings and reviews"""
    __tablename__ = "ratings"
    
    rating = Column(Integer, nullable=False)  # 1-5 rating
    review = Column(Text, nullable=True)
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    coffee_id = Column(UUID(as_uuid=True), ForeignKey("coffee_menu.id"), nullable=False)
    
    # Relationships
    user = relationship("UserModel", back_populates="ratings")
    coffee = relationship("CoffeeMenuModel", back_populates="ratings")
    
    def __repr__(self):
        return f"<Rating {self.id}>"