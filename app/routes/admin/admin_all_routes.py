from fastapi import APIRouter
from app.routes.admin import (
    admin_booking_management_routes, 
    admin_coffee_management_routes,
    booking_status_routes,
    admin_order_management_routes,
    admin_analitics_statistics
)

router = APIRouter()

router.include_router(admin_coffee_management_routes.router)
router.include_router(admin_booking_management_routes.router)
router.include_router(booking_status_routes.router)
router.include_router(admin_booking_management_routes.router)
router.include_router(admin_analitics_statistics.router)