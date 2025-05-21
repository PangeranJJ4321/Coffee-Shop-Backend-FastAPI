from fastapi import APIRouter
from app.routes.user import (
    booking_routes,
    menu_routes,
    order_routes,
    payment_routes,
    rating_routes
)

router = APIRouter()

router.include_router(booking_routes.router)
router.include_router(menu_routes.router)
router.include_router(order_routes.router)
router.include_router(payment_routes.router)
router.include_router(rating_routes.router)