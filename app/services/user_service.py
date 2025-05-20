from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from app.core.database import get_db
from app.models.user import UserModel, Role, RoleModel
from app.schemas.user_schema import UserUpdate, UserProfile
from app.utils.security import get_password_hash

class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
    
    def get_user_by_id(self, user_id: UUID) -> Optional[UserModel]:
        """Get user by ID"""
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get user by email"""
        return self.db.query(UserModel).filter(UserModel.email == email).first()
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserModel]:
        """Get list of users with pagination"""
        return self.db.query(UserModel).offset(skip).limit(limit).all()
    
    def update_user(self, user_id: UUID, user_data: UserUpdate, current_user: UserModel) -> UserModel:
        """Update user details"""
        # Check if user exists
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        # Check if user has permission to update (must be admin or the user themselves)
        if current_user.id != user_id and current_user.role.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this user"
            )
        
        # Update fields
        if user_data.name:
            user.name = user_data.name
        if user_data.phone_number:
            user.phone_number = user_data.phone_number
        if user_data.password and current_user.id == user_id:  # Only allow password change for own account
            user.password_hash = get_password_hash(user_data.password)
        
        # Save changes
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_profile(self, user_id: UUID) -> UserProfile:
        """Get user profile with favorites and other related data"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        return UserProfile(
            id=user.id,
            name=user.name,
            email=user.email,
            phone_number=user.phone_number,
            role=user.role.role,
            favorites=[
                {
                    "id": fav.coffee.id,
                    "name": fav.coffee.name,
                    "price": fav.coffee.price,
                    "image_url": fav.coffee.image_url
                } for fav in user.favorites
            ],
            bookings_count=len(user.bookings),
            orders_count=len(user.orders)
        )
    
    def get_admin_users(self) -> List[UserModel]:
        """Get all admin users"""
        admin_role = self.db.query(RoleModel).filter(RoleModel.role == Role.ADMIN).first()
        if not admin_role:
            return []
        
        return self.db.query(UserModel).filter(UserModel.role_id == admin_role.id).all()
    
    def set_role(self, user_id: UUID, role: Role, current_user: UserModel) -> UserModel:
        """Set user role (admin only)"""
        # Check if requester is admin
        if current_user.role.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can change user roles"
            )
        
        # Get target user
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        # Get or create role
        db_role = self.db.query(RoleModel).filter(RoleModel.role == role).first()
        if not db_role:
            db_role = RoleModel(role=role)
            self.db.add(db_role)
            self.db.commit()
            self.db.refresh(db_role)
        
        # Update user role
        user.role_id = db_role.id
        self.db.commit()
        self.db.refresh(user)
        
        return user