"""
Authentication service handling all authentication-related operations
"""
from typing import Optional, Dict, Any
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db
from app.utils.security import verify_password, get_password_hash, create_access_token, decode_jwt_token
from app.models.user import UserModel, RoleModel, Role
from app.schemas.auth_schema import UserLogin, TokenResponse, UserRegister

class AuthService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
    
    def authenticate_user(self, login_data: UserLogin) -> Optional[UserModel]:
        """Authenticate user with email and password"""
        user = self.db.query(UserModel).filter(UserModel.email == login_data.email).first()
        
        if not user:
            return None
            
        if not verify_password(login_data.password, user.password_hash):
            return None
            
        return user
    
    def create_access_token_for_user(self, user: UserModel) -> TokenResponse:
        """Create access token for user"""
        user_data = {
            "sub": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": user.role.role.value
        }
        
        token = create_access_token(user_data)
        return TokenResponse(
            access_token=token,
            token_type="bearer"
        )
    
    def register_user(self, user_data: UserRegister) -> UserModel:
        """Register a new user"""
        try:
            # Get the user role (default to USER)
            user_role = self.db.query(RoleModel).filter(RoleModel.role == Role.USER).first()
            if not user_role:
                # Create role if it doesn't exist
                user_role = RoleModel(role=Role.USER)
                self.db.add(user_role)
                self.db.commit()
                self.db.refresh(user_role)
            
            # Create new user with password hash
            password_hash = get_password_hash(user_data.password)
            
            new_user = UserModel(
                name=user_data.name,
                email=user_data.email,
                phone_number=user_data.phone_number,
                password_hash=password_hash,
                role_id=user_role.id
            )
            
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            return new_user
            
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token"""
        try:
            payload = decode_jwt_token(token)
            user_id = payload.get("sub")
            
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            return payload
            
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )