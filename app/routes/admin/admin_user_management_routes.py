from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.controllers.admin_user_management import UserController 
from app.schemas.auth_schema import UserRegister
from app.schemas.user_schema import  UserCreate, UserUpdate, UserResponse 
from app.models.user import UserModel 
from app.utils.security import get_current_admin_user 

router = APIRouter(prefix="/user-management", tags=["Admin ~ User Management"])

@router.get("/users", response_model=List[UserResponse], summary="Get all users (Admin only)")
def get_all_users_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=200),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user) 
):
    controller = UserController(db) # Inisialisasi controller dengan db
    return controller.get_users(skip=skip, limit=limit)

@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Create a new user (Admin only)")
def create_user_admin(
    user_create: UserCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    controller = UserController(db)
    return controller.create_user(user_create)

@router.put("/users/{user_id}", response_model=UserResponse, summary="Update user details (Admin only)")
def update_user_admin(
    user_id: UUID,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    controller = UserController(db)
    return controller.update_user_by_admin(user_id, user_update)

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user (Admin only)")
def delete_user_admin(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    controller = UserController(db)
    controller.delete_user(user_id)
    return None # No content for 204