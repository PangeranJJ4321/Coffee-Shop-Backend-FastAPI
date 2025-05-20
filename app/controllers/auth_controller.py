from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.schemas.auth_schema import EmailVerification, ResendVerification, UserLogin, UserRegister, UserResponse
from app.services.auth_services import AuthService


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
    user,_ = auth_service.register_user(user_data)

    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        phone_number=user.phone_number,
        role=user.role.role
    )

def verify_email_controller(verification_data: EmailVerification, auth_service: AuthService):
    """
    Controller for verifying email using a token
    """
    token = verification_data.token
    user = auth_service.validate_token(token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    return {"message": "Email successfully verified."}


def resend_verification_controller(resend_data: ResendVerification, auth_service: AuthService):
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