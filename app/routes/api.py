from fastapi import APIRouter

from app.routes import auth_routes
from app.routes import users_routes


api_router = APIRouter()
api_router.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users_routes.router, prefix="/users", tags=["Users"])