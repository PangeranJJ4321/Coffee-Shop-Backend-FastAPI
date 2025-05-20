from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.controllers.auth_controller import login_controller
from app.schemas.auth_schema import TokenResponse, UserRegister, UserResponse
from app.services.auth_services import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends()
):
    return login_controller(form_data, auth_service)


@router.post("/register", response_model=UserResponse)
def register(
    user_data: UserRegister,
):
    return 