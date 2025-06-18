# app/services/user_service.py - DIREVISI
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from fastapi import Depends, HTTPException, status

from app.core.database import get_db
from app.models.notification import UserFavoriteModel
from app.models.user import UserModel, Role
from app.schemas.user_schema import UserUpdate, UserProfile, CoffeeMenuPublicResponse # Import CoffeeMenuPublicResponse
from app.utils.security import get_password_hash
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from app.services.order_service import order_service

class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)
        self.order_service = order_service

    def get_user_by_id(self, user_id: UUID) -> Optional[UserModel]:
        """Get user by ID"""
        # Load relationships yang dibutuhkan oleh UserProfile
        return self.db.query(UserModel).options(
            joinedload(UserModel.role),
            joinedload(UserModel.favorites).joinedload(UserFavoriteModel.coffee), # Load coffee details untuk favorites
            joinedload(UserModel.bookings),
            joinedload(UserModel.orders)
        ).filter(UserModel.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get user by email"""
        return self.user_repository.get_by_email(email)
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserModel]:
        """Get list of users with pagination"""
        return self.user_repository.get_all(skip, limit)
    
    def update_user(self, user_id: UUID, user_data: UserUpdate, current_user: UserModel) -> UserModel:
        """Update user details"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        if current_user.id != user_id and current_user.role.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this user"
            )
        
        update_data = {}
        if user_data.name:
            update_data["name"] = user_data.name
        if user_data.phone_number is not None: # Penting: izinkan phone_number diset null
            update_data["phone_number"] = user_data.phone_number
        if user_data.password:
            update_data["password_hash"] = get_password_hash(user_data.password)
        
        return self.user_repository.update(user, update_data)
    
    def get_user_profile(self, user_id: UUID) -> UserProfile:
        """Get user profile with favorites and other related data"""
        user = self.get_user_by_id(user_id) # Sudah di-load dengan relations
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        order_stats = self.order_service.get_order_statistics(self.db, user_id)

        # Map favorites ke CoffeeMenuPublicResponse
        user_favorites_mapped = []
        for fav_item in user.favorites:
            coffee_menu = fav_item.coffee
            if coffee_menu: # Pastikan objek kopi ada
                # Asumsi average_rating dan total_ratings di CoffeeMenuModel sudah diupdate
                user_favorites_mapped.append(CoffeeMenuPublicResponse(
                    id=coffee_menu.id,
                    name=coffee_menu.name,
                    price=coffee_menu.price,
                    description=coffee_menu.description,
                    image_url=coffee_menu.image_url,
                    is_available=coffee_menu.is_available,
                    rating_average=coffee_menu.average_rating,
                    rating_count=coffee_menu.total_ratings,
                    is_favorite=True, # Karena ini dari daftar favorit user
                    coffee_shop_id=coffee_menu.coffee_shop_id,
                    coffee_shop_name=coffee_menu.coffee_shop.name, # Akses nama coffee shop
                    category=coffee_menu.category,
                    tags=coffee_menu.tags
                ))


        return UserProfile(
            id=user.id,
            name=user.name,
            email=user.email,
            phone_number=user.phone_number,
            role=user.role.role,
            is_verified=user.is_verified, # Pastikan ini ada
            
            favorites=user_favorites_mapped, # Gunakan data favorit yang sudah di-map
            bookings_count=len(user.bookings),
            orders_count=len(user.orders),
            
            orders_created_count=order_stats["orders_created"],
            orders_paid_for_others_count=order_stats["orders_paid_for_others"],
            orders_paid_by_others_count=order_stats["orders_paid_by_others"],
            total_spent_amount=order_stats["total_spent"],
            average_order_value=order_stats["average_order_value"], # Tambahkan AOV

            member_since=user.created_at # Tanggal bergabung
        )
    
    def get_admin_users(self) -> List[UserModel]:
        """Get all admin users"""
        return self.user_repository.get_users_by_role(Role.ADMIN)
    
    def set_role(self, user_id: UUID, role: Role, current_user: UserModel) -> UserModel:
        """Set user role (admin only)"""
        if current_user.role.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can change user roles"
            )
        
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        
        return self.user_repository.set_user_role(user, role)