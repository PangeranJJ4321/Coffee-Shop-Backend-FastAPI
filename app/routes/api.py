from fastapi import APIRouter

from app.routes.endpoints import auth_routes
from app.routes.endpoints.users import users


api_router = APIRouter()
api_router.include_router(auth_routes.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])