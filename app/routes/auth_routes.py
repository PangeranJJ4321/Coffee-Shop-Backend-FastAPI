from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.controllers.auth_controller import (
    login_controller, 
    register_controller, 
    verify_email_controller, 
    resend_verification_controller,
    forgot_password_controller,
    reset_password_controller
)
from app.models.user import UserModel
from app.schemas.auth_schema import (
    TokenResponse, 
    UserLogin, 
    UserRegister, 
    UserResponse, 
    EmailVerification, 
    ResendVerification,
    PasswordReset,
    PasswordResetConfirm
)
from app.schemas.user_schema import PasswordChange
from app.services.auth_services import AuthService
from app.utils.security import get_current_user

router = APIRouter()

@router.post("/login", response_model=TokenResponse)
def login(
    form_data: UserLogin,
    auth_service: AuthService = Depends()
):
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    return login_controller(form_data, auth_service)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserRegister,
    auth_service: AuthService = Depends()
):
    """
    Register new user
    """
    return register_controller(user_data, auth_service)


@router.post("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(
    verification_data: EmailVerification,
    auth_service: AuthService = Depends()
):
    """
    Verify user email with token
    """
    return verify_email_controller(verification_data, auth_service)


@router.post("/resend-verification", status_code=status.HTTP_200_OK)
def resend_verification(
    resend_data: ResendVerification,
    auth_service: AuthService = Depends()
):
    """
    Resend verification email
    """
    return resend_verification_controller(resend_data, auth_service)


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(
    reset_data: PasswordReset,
    auth_service: AuthService = Depends()
):
    """
    Send password reset email
    """
    return forgot_password_controller(reset_data, auth_service)


@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    reset_data: PasswordResetConfirm,
    auth_service: AuthService = Depends()
):
    """
    Reset password with token
    """
    return reset_password_controller(reset_data, auth_service)

@router.put("/change-password", status_code=status.HTTP_200_OK) # <-- TAMBAHKAN INI
def change_password_route(
    password_data: PasswordChange,
    auth_service: AuthService = Depends(),
    current_user: UserModel = Depends(get_current_user) 
):
    success = auth_service.change_password(
        current_user.id,
        password_data.current_password,
        password_data.new_password
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password"
        )
    return {"message": "Password successfully changed."}