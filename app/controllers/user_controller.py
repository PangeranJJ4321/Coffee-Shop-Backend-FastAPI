from fastapi import Depends, HTTPException, status
from app.models.user import Role, UserModel
from app.schemas.user_schema import UserResponse
from app.services.user_service import UserService


def get_current_user_profile(
    current_user : UserModel,
    user_service : UserService = Depends()
) :
    return user_service.get_user_profile(current_user.id)


def get_user(
    user_id,
    current_user : UserModel,
    user_service : UserService = Depends()
):
    """Get user by ID (admin can get any user, users can only get themselves)"""
    # Check if user has permission
    if current_user.id != user_id and current_user.role.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user information"
        )
    
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found"
        )
    
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        phone_number=user.phone_number,
        role=user.role.role,
        is_verified=user.is_verified
    )