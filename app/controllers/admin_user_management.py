from typing import List, Optional
from uuid import UUID
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth_schema import UserRegister
from app.services.user_service import UserService 
from app.schemas.user_schema import UserUpdate, UserResponse # Import schemas

class UserController:
    def __init__(self, db: Session = Depends(get_db)): # Injeksi db ke controller
        self.service = UserService(db) 

    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        users = self.service.get_users(skip, limit)
        return users

    def create_user(self, user_create: UserRegister) -> UserResponse:
        return self.service.create_user(user_create) 

    def get_user_by_id(self, user_id: UUID) -> UserResponse:
        user = self.service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def update_user_by_admin(self, user_id: UUID, user_data: UserUpdate) -> UserResponse:
        return self.service.update_user_by_admin(user_id, user_data) # Teruskan db

    def delete_user(self, user_id: str) -> None:
        self.service.delete_user(user_id) 