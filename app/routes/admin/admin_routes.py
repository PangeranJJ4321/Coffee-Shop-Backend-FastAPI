"""
Admin router for admin-only endpoints
"""
from fastapi import APIRouter

from app.routes.admin import (
    coffee_menu_routes, 
    variant_type_routes, 
    variant_routes, 
    coffee_variant_routes
) 
router = APIRouter(prefix="/menu-management")

# Include admin menu management routes
router.include_router(coffee_menu_routes.router)
router.include_router(variant_type_routes.router)
router.include_router(variant_routes.router)
router.include_router(coffee_variant_routes.router)