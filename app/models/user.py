"""
User model with support for Supabase Auth
"""
import enum
from sqlalchemy import Column, String, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class Role(enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER" 
    GUEST = "GUEST"

class RoleModel(BaseModel):
    __tablename__ = "roles"
    
    role = Column(Enum(Role), unique=True, nullable=False)
    
    # Relationships
    users = relationship("UserModel", back_populates="role")
    
    def __repr__(self):
        return f"<Role {self.role}>"

class UserModel(BaseModel):
    """User model with Supabase Auth integration"""
    __tablename__ = "users"
    
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String, nullable=True)
    
    # Supabase User ID for reference
    supabase_uid = Column(String, unique=True, nullable=True)
    
    # Foreign keys
    role_id = Column(UUID(as_uuid=True), ForeignKey("roles.id"), nullable=False)
    
    # Relationships
    role = relationship("RoleModel", back_populates="users")
    orders = relationship("OrderModel", back_populates="user", foreign_keys="[OrderModel.user_id]")
    paid_orders = relationship("OrderModel", back_populates="paid_by_user", foreign_keys="[OrderModel.paid_by_user_id]")
    bookings = relationship("BookingModel", back_populates="user")
    favorites = relationship("UserFavoriteModel", back_populates="user")
    ratings = relationship("RatingModel", back_populates="user")
    notifications = relationship("NotificationModel", back_populates="user")
    payouts = relationship("PayoutModel", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.email}>"