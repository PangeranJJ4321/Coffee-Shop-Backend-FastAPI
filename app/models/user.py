# app/models/user.py - (Hanya untuk konfirmasi, tidak ada perubahan kode di sini)
import enum
from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, Enum, Boolean, DateTime
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
    __tablename__ = "users"
    
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String, nullable=True)
    
    # Authentication fields
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String, nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)
    last_login = Column(DateTime, nullable=True)

    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

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
    
    @property
    def role_enum(self) -> Role:
        """Return role as enum value"""
        if self.role and hasattr(self.role, 'role'):
            return Role(self.role.role)
        return Role.USER  # default
    
    def __repr__(self):
        return f"<User {self.email}>"