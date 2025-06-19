"""
Authentication service handling all authentication-related operations
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from uuid import UUID
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.database import get_db
from app.utils.security import verify_password, get_password_hash, create_access_token, decode_jwt_token, create_verification_token
from app.models.user import UserModel, Role
from app.schemas.auth_schema import UserLogin, TokenResponse, UserRegister
from app.repositories.user_repository import UserRepository
from app.repositories.role_repository import RoleRepository
from app.services.email import send_verification_email, send_password_reset_email

class AuthService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.user_repository = UserRepository(db)
        self.role_repository = RoleRepository(db)
    
    def authenticate_user(self, login_data: UserLogin) -> Optional[UserModel]:
        """Authenticate user with email and password"""
        user = self.user_repository.get_by_email(login_data.email)
        
        if not user:
            return None
            
        if not verify_password(login_data.password, user.password_hash):
            return None
        
        user.last_login = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        
        # Check if user is verified
        if not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not verified. Please check your inbox for the verification email."
            )
            
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
    
    def register_user(self, user_data: UserRegister) -> Tuple[UserModel, str]:
        """Register a new user and generate verification token"""
        try:
            # Check if user already exists
            existing_user = self.user_repository.get_by_email(user_data.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email already exists"
                )
            
            # Get or create user role
            user_role = self.role_repository.get_or_create(Role.USER)
            
            # Create password hash
            password_hash = get_password_hash(user_data.password)
            
            # Create user object
            new_user_data = {
                "name": user_data.name,
                "email": user_data.email,
                "phone_number": user_data.phone_number,
                "password_hash": password_hash,
                "role_id": user_role.id,
                "is_verified": True  
            }
            
            # Create new user
            new_user = self.user_repository.create(new_user_data)
            
            # Generate verification token
            token = create_verification_token()
            expires_at = datetime.utcnow() + timedelta(hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS)
            
            # Save verification token
            self.user_repository.set_verification_token(new_user, token, expires_at)
            
            # Send verification email
            send_verification_email(new_user.email, token)
            
            return new_user, token
            
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists"
            )
    
    def verify_email(self, token: str) -> bool:
        """Verify user email with token"""
        # Find user with this verification token
        user = self.db.query(UserModel).filter(UserModel.verification_token == token).first()
        
        if not user:
            return False
        
        # Check if token is expired
        if user.verification_token_expires < datetime.utcnow():
            return False
        
        # Mark user as verified
        self.user_repository.update_verification(user, True)
        return True
    
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
            
            # Check if user exists and is active
            user = self.user_repository.get(UUID(user_id))
            if not user or not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User is inactive or deleted",
                    headers={"WWW-Authenticate": "Bearer"},
                )
                
            return payload
            
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def resend_verification_email(self, email: str) -> bool:
        """Resend verification email"""
        user = self.user_repository.get_by_email(email)
        
        if not user:
            # Don't reveal if user exists or not for security
            return True
        
        if user.is_verified:
            # User is already verified
            return True
        
        # Generate new verification token
        token = create_verification_token()
        expires_at = datetime.utcnow() + timedelta(hours=settings.VERIFICATION_TOKEN_EXPIRE_HOURS)
        
        # Save verification token
        self.user_repository.set_verification_token(user, token, expires_at)
        
        # Send verification email
        return send_verification_email(user.email, token)
    
    def send_password_reset_email(self, email: str) -> bool:
        """Send password reset email"""
        user = self.user_repository.get_by_email(email)
        
        if not user:
            # Don't reveal if user exists or not for security
            return True
        
        if not user.is_verified:
            # User must be verified to reset password
            return True
        
        # Generate password reset token
        reset_token = create_verification_token()
        expires_at = datetime.utcnow() + timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
        
        # Save reset token
        self.user_repository.set_password_reset_token(user, reset_token, expires_at)
        
        # Send password reset email
        return send_password_reset_email(user.email, reset_token)
    
    def reset_password(self, token: str, new_password: str) -> bool:
        """Reset user password with token"""
        # Find user with this reset token
        user = self.db.query(UserModel).filter(UserModel.reset_token == token).first()
        
        if not user:
            return False
        
        # Check if token is expired
        if not user.reset_token_expires or user.reset_token_expires < datetime.utcnow():
            return False
        
        # Hash new password
        password_hash = get_password_hash(new_password)
        
        # Update password and clear reset token
        self.user_repository.update_password(user, password_hash)
        self.user_repository.clear_password_reset_token(user)
        
        return True
    
    def change_password(self, user_id: UUID, current_password: str, new_password: str) -> bool:
        """Change user's password after verifying current password"""
        user = self.user_repository.get(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Verifikasi password saat ini
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

        # Hash password baru
        new_password_hash = get_password_hash(new_password)

        # Update password di database
        self.user_repository.update_password(user, new_password_hash)
        return True