# app/controllers/auth_controller.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth_schema import (
    EmailVerification, 
    ResendVerification, 
    UserLogin, 
    UserRegister, 
    UserResponse,
    PasswordReset,
    PasswordResetConfirm
)
from app.services.auth_services import AuthService


def login_controller(
    form_data : UserLogin,
    auth_service : AuthService = Depends()
) :
    login_data = UserLogin(email=form_data.email, password=form_data.password)
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
    user,_ = auth_service.register_user(user_data)

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        phone_number=user.phone_number,
        role=user.role.role
    )

def verify_email_controller(
    verification_data: EmailVerification,
    auth_service: AuthService = Depends()
):
    """
    Controller for verifying email using a token
    """
    token = verification_data.token
    # Use the correct verification method
    success = auth_service.verify_email(token)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    return {"message": "Email successfully verified."}


def resend_verification_controller(
    resend_data: ResendVerification,
    auth_service: AuthService = Depends()
):
    """
    Controller for resending email verification
    """
    email = resend_data.email
    result = auth_service.resend_verification_email(email)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or already verified"
        )
    
    return {"message": "Verification email sent."}


def forgot_password_controller(
    reset_data: PasswordReset,
    auth_service: AuthService = Depends()
):
    """
    Controller for initiating password reset process
    """
    email = reset_data.email
    result = auth_service.send_password_reset_email(email)
    
    # Always return success message for security reasons
    # Don't reveal whether the email exists in the system
    return {"message": "If an account with that email exists, a password reset link has been sent."}


def reset_password_controller(
    reset_data: PasswordResetConfirm,
    auth_service: AuthService = Depends()
):
    """
    Controller for confirming password reset with token
    """
    success = auth_service.reset_password(reset_data.token, reset_data.password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return {"message": "Password successfully reset."}