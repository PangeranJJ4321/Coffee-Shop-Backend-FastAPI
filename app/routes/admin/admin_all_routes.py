from fastapi import APIRouter
from app.routes.admin import admin_booking_management_routes, admin_coffee_management_routes

router = APIRouter()

router.include_router(admin_coffee_management_routes.router)
router.include_router(admin_booking_management_routes.router)