from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from app.core.database import get_db
from app.models.user import UserModel, Role
from app.schemas.user_schema import UserUpdate, UserProfile
from app.utils.security import get_password_hash
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository

class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)
    
    def get_user_by_id(self, user_id: UUID) -> Optional[UserModel]:
        """Get user by ID"""
        return self.user_repository.get(user_id)
    
    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get user by email"""
        return self.user_repository.get_by_email(email)
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserModel]:
        """Get list of users with pagination"""
        return self.user_repository.get_all(skip, limit)
    
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
        
        # Prepare update data
        update_data = {}
        if user_data.name:
            update_data["name"] = user_data.name
        if user_data.phone_number:
            update_data["phone_number"] = user_data.phone_number
        if user_data.password and current_user.id == user_id:  # Only allow password change for own account
            update_data["password_hash"] = get_password_hash(user_data.password)
        
        # Update user
        return self.user_repository.update(user, update_data)
    
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
        return self.user_repository.get_users_by_role(Role.ADMIN)
    
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
        
        # Update user role
        return self.user_repository.set_user_role(user, role)