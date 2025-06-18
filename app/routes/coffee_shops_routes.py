# app/routes/coffee_shops_routes.py
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Response, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import UserModel
from app.schemas.coffe_shop_schema import CoffeeShopCreate, CoffeeShopUpdate, CoffeeShopResponse
from app.services.coffee_shop_service import CoffeeShopService 
from app.utils.security import get_current_user, get_current_admin_user

router = APIRouter(prefix="/coffee-shops", tags=["Coffee Shops"])

# Helper dependency untuk mendapatkan instance service
def get_coffee_shop_service(db: Session = Depends(get_db)) -> CoffeeShopService:
    return CoffeeShopService(db)

# Admin Endpoints
@router.post("/", response_model=CoffeeShopResponse, status_code=status.HTTP_201_CREATED)
async def create_coffee_shop(
    coffee_shop_data: CoffeeShopCreate,
    current_user: UserModel = Depends(get_current_admin_user),
    service: CoffeeShopService = Depends(get_coffee_shop_service) # <-- Inject service melalui Depends
):
    """Create a new coffee shop (Admin only)"""
    return service.create_coffee_shop(coffee_shop_data)

@router.put("/{coffee_shop_id}", response_model=CoffeeShopResponse)
async def update_coffee_shop(
    coffee_shop_id: UUID,
    coffee_shop_data: CoffeeShopUpdate,
    current_user: UserModel = Depends(get_current_admin_user),
    service: CoffeeShopService = Depends(get_coffee_shop_service) # <-- Inject service
):
    """Update a coffee shop by ID (Admin only)"""
    return service.update_coffee_shop(coffee_shop_id, coffee_shop_data)

@router.delete("/{coffee_shop_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coffee_shop(
    coffee_shop_id: UUID,
    current_user: UserModel = Depends(get_current_admin_user),
    service: CoffeeShopService = Depends(get_coffee_shop_service) # <-- Inject service
):
    """Delete a coffee shop by ID (Admin only)"""
    service.delete_coffee_shop(coffee_shop_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Public/User Endpoints
@router.get("/", response_model=List[CoffeeShopResponse])
async def get_all_coffee_shops(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=200),
    service: CoffeeShopService = Depends(get_coffee_shop_service) # <-- Inject service
):
    """Get all registered coffee shops"""
    return service.get_all_coffee_shops(skip, limit)

@router.get("/{coffee_shop_id}", response_model=CoffeeShopResponse)
async def get_coffee_shop_by_id(
    coffee_shop_id: UUID,
    service: CoffeeShopService = Depends(get_coffee_shop_service) 
):
    """Get a coffee shop by ID"""
    return service.get_coffee_shop_by_id(coffee_shop_id)