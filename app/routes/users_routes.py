from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.utils.security import get_current_user, get_current_admin_user
from app.services.user_service import UserService
from app.models.user import UserModel, Role
from app.schemas.user_schema import (
    UserBase,
    UserResponse, 
    UserUpdate, 
    UserProfile, 
    UserRoleUpdate
)

from app.controllers import user_controller

router = APIRouter()

@router.get("/me", response_model=UserProfile)
def get_current_user_profile(
    current_user: UserModel = Depends(get_current_user),
    user_service: UserService = Depends()
):
    return user_controller.get_current_user_profile(current_user, user_service)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    current_user: UserModel = Depends(get_current_user),
    user_service: UserService = Depends()
):
    return user_controller.get_user(user_id, current_user, user_service)
    

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    user_service: UserService = Depends()
):
    """Update user information"""
    updated_user = user_service.update_user(user_id, user_data, current_user)
    return UserResponse(
        id=updated_user.id,
        name=updated_user.name,
        email=updated_user.email,
        phone_number=updated_user.phone_number,
        role=updated_user.role.role,
        is_verified=updated_user.is_verified
    )

@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_admin_user),
    user_service: UserService = Depends()
):
    """Get all users (admin only)"""
    users = user_service.get_users(skip, limit)
    return [
        UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone_number=user.phone_number,
            role=user.role.role,
            is_verified=user.is_verified
        ) for user in users
    ]

@router.patch("/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: UUID,
    role_data: UserRoleUpdate,
    current_user: UserModel = Depends(get_current_admin_user),
    user_service: UserService = Depends()
):
    updated_user = user_service.set_role(user_id, role_data.role, current_user)
    return UserResponse(
        id=updated_user.id,
        name=updated_user.name,
        email=updated_user.email,
        phone_number=updated_user.phone_number,
        role=updated_user.role.role
    )