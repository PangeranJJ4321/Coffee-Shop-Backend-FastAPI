from fastapi import APIRouter
from app.routes import auth_routes
from app.routes import users_routes
from app.routes.admin import admin_all_routes

api_router = APIRouter()

# Auth
api_router.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
# Users
api_router.include_router(users_routes.router, prefix="/users", tags=["Users"])
# Admin
api_router.include_router(admin_all_routes.router, prefix="/admin")
