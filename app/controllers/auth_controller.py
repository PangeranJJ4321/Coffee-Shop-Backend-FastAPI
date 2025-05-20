from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth_schema import UserLogin, UserRegister, UserResponse
from app.services.auth_services import AuthService
from app.services.user_service import UserService


def login_controller(
    form_data : OAuth2PasswordRequestForm = Depends(),
    auth_service : AuthService = Depends()
) :
    login_data = UserLogin(email=form_data.username, password=form_data.password)
    user = auth_service.authenticate_user(login_data)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return auth_service.create_access_token_for_user(user)


def register_controller(
    user_data : UserRegister,
    auth_service : AuthService = Depends()

):
    user = auth_service.register_user(user_data)

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        phone_number=user.phone_number,
        role=user.role.role
    )