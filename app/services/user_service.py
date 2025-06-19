from typing import List, Optional
from uuid import UUID
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, joinedload, relationship
from fastapi import Depends, HTTPException, status

from app.core.database import get_db
from app.models.coffee import CoffeeMenuModel
from app.models.notification import UserFavoriteModel
from app.models.order import OrderModel, OrderStatus
from app.models.user import UserModel, Role
from app.schemas.auth_schema import UserRegister
from app.schemas.user_schema import UserCreate, UserUpdate, UserProfile, CoffeeMenuPublicResponse # Import CoffeeMenuPublicResponse
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
            joinedload(UserModel.favorites).joinedload(UserFavoriteModel.coffee).joinedload(CoffeeMenuModel.coffee_shop), 
            joinedload(UserModel.bookings),
            joinedload(UserModel.orders)
        ).filter(UserModel.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        """Get user by email"""
        return self.user_repository.get_by_email(email)
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserModel]:
        """Get list of users with pagination"""
        users_query = self.db.query(UserModel).options(joinedload(UserModel.role)).offset(skip).limit(limit)
        users = users_query.all()

        user_ids = [user.id for user in users]
        if not user_ids: 
            return []
        
        order_stats_query = self.db.query(
            OrderModel.user_id,
            OrderModel.paid_by_user_id,
            func.count(OrderModel.id).label("order_count"),
            func.sum(OrderModel.total_price).label("total_price_sum")
        ).filter(
            and_(
                (OrderModel.user_id.in_(user_ids) | (OrderModel.paid_by_user_id.in_(user_ids))),
                OrderModel.status == OrderStatus.COMPLETED 
            )
        ).group_by(OrderModel.user_id, OrderModel.paid_by_user_id).all()

        user_stats_map = {user_id: {"total_orders_count": 0, "total_spent_amount": 0} for user_id in user_ids}

        for row in order_stats_query:
            if row.user_id in user_stats_map:
                user_stats_map[row.user_id]["total_orders_count"] += (row.order_count or 0)

            if row.paid_by_user_id in user_stats_map:
                # This counts money *spent* by the user.
                user_stats_map[row.paid_by_user_id]["total_spent_amount"] += (row.total_price_sum or 0)

        # Assign computed stats to UserModel instances (these are transient attributes for Pydantic mapping)
        for user in users:
            stats = user_stats_map.get(user.id, {})
            user.total_orders_count = stats.get("total_orders_count", 0)
            user.total_spent_amount = int(stats.get("total_spent_amount", 0)) # Pastikan integer
            user.status = 'ACTIVE' if user.is_active else 'INACTIVE'

            if hasattr(user.role, 'role'):
                # Jika role adalah object dengan attribute role
                user.role_value = user.role.role
            else:
                # Jika role sudah berupa enum
                user.role_value = user.role
         

        return users


    def create_user(self, user_create: UserCreate) -> UserModel:
        """Create a new user"""
        if self.user_repository.get_by_email(user_create.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        role_obj = self.role_repository.get_by_role(user_create.role.value)
        if not role_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Role '{user_create.role.value}' not found."
            )

        hashed_password = get_password_hash(user_create.password)

        new_user = UserModel(
            name=user_create.name,
            email=user_create.email,
            phone_number=user_create.phone_number,
            password_hash=hashed_password,
            role_id=role_obj.id,
            is_verified=True, # harusnya False Verify email dulu di email user.
            is_active=True 
        )
        return self.user_repository.create(new_user)
    
    def update_user_by_admin(self, user_id: UUID, user_data: UserUpdate) -> UserModel:
        """Update user details by admin"""
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )

        update_data = user_data.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            user.password_hash = get_password_hash(update_data["password"])
        
        if "role" in update_data and update_data["role"]:
            new_role_obj = self.role_repository.get_by_role(update_data["role"].value)
            if not new_role_obj:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found.")
            user.role_id = new_role_obj.id

        if "status" in update_data: 
            user.is_active = update_data["status"]

        if "name" in update_data: user.name = update_data["name"]
        if "email" in update_data: user.email = update_data["email"]
        if "phone_number" in update_data: user.phone_number = update_data["phone_number"]


        self.db.commit()
        self.db.refresh(user) # Refresh user to get updated data, including role relationship
        return user

    
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
            is_active=user.is_active, 
            created_at=user.created_at, 
            updated_at=user.updated_at, 
            last_login=user.last_login, 
            
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
    
    def delete_user(self, user_id: UUID) -> None:
        self.user_repository.delete(user_id)