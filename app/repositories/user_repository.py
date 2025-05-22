from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.user import UserModel, RoleModel, Role
from app.repositories.base_repository import BaseRepository
from app.schemas.auth_schema import UserRegister
from app.schemas.user_schema import UserUpdate

class UserRepository(BaseRepository[UserModel, UserRegister, UserUpdate]):
    """Repository for User model operations"""
    
    def __init__(self, db: Session):
        super().__init__(UserModel, db)
        
    def get_by_email(self, email: str) -> Optional[UserModel]:
        """Get user by email"""
        return self.db.query(UserModel).filter(UserModel.email == email).first()
    
    def get_users_by_role(self, role: Role) -> List[UserModel]:
        """Get all users with a specific role"""
        role_obj = self.db.query(RoleModel).filter(RoleModel.role == role).first()
        if not role_obj:
            return []
        return self.db.query(UserModel).filter(UserModel.role_id == role_obj.id).all()
    
    def update_verification(self, user: UserModel, is_verified: bool) -> UserModel:
        """Update user verification status"""
        user.is_verified = is_verified
        user.verification_token = None
        user.verification_token_expires = None
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def set_verification_token(self, user: UserModel, token: str, expires_at) -> UserModel:
        """Set verification token for user"""
        user.verification_token = token
        user.verification_token_expires = expires_at
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def set_user_role(self, user: UserModel, role: Role) -> UserModel:
        """Set user role"""
        # Get or create role
        role_obj = self.db.query(RoleModel).filter(RoleModel.role == role).first()
        if not role_obj:
            role_obj = RoleModel(role=role)
            self.db.add(role_obj)
            self.db.commit()
            self.db.refresh(role_obj)
        
        # Update user role
        user.role_id = role_obj.id
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def set_password_reset_token(self, user: UserModel, token: str, expires_at: datetime) -> None:
        """Set password reset token for user"""
        user.reset_token = token
        user.reset_token_expires = expires_at
        self.db.commit()
        self.db.refresh(user)

    def clear_password_reset_token(self, user: UserModel) -> None:
        """Clear password reset token for user"""
        user.reset_token = None
        user.reset_token_expires = None
        self.db.commit()
        self.db.refresh(user)

    def update_password(self, user: UserModel, password_hash: str) -> None:
        """Update user password"""
        user.password_hash = password_hash
        self.db.commit()
        self.db.refresh(user)