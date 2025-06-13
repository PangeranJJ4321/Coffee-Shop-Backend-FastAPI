from fastapi import APIRouter
from app.routes import auth_routes, coffee_shops_routes
from app.routes import users_routes
from app.routes.admin import admin_all_routes
from app.routes.user import user_all_routes

api_router = APIRouter()

# Auth
api_router.include_router(auth_routes.router, prefix="/auth", tags=["Auth"])
# Users
api_router.include_router(users_routes.router, prefix="/users", tags=["Users"])
# Fitur Admin
api_router.include_router(admin_all_routes.router, prefix="/admin")
# Coffee Shope
api_router.include_router(coffee_shops_routes.router, tags=["Coffee Shops"]) # <-- Tambahkan ini


# Fitur User
api_router.include_router(user_all_routes.router)