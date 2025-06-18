"""
Routes for user-facing coffee menu
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import UserModel
from app.schemas.coffee_schema import (
    CoffeeMenuPublicResponse,
    CoffeeMenuDetailResponse,
    CoffeeFilter
)
from app.services.coffee_menu_service import coffee_menu_service
from app.utils.security import get_current_user

router = APIRouter(prefix="/menu", tags=["Coffee Menu"])

@router.get("/coffee-shops/{coffee_shop_id}/menu", response_model=List[CoffeeMenuPublicResponse])
async def get_coffee_shop_menu(
    coffee_shop_id: UUID,
    filter_params: CoffeeFilter = Depends(),
    db: Session = Depends(get_db)
):
    """Get all available coffee menu items for a specific coffee shop with optional filtering"""
    return coffee_menu_service.get_public_menu(db, coffee_shop_id, filter_params)

@router.get("/coffee/{coffee_id}", response_model=CoffeeMenuDetailResponse)
async def get_coffee_details(
    coffee_id: UUID,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific coffee menu item"""
    coffee = coffee_menu_service.get_coffee_details(db, coffee_id)
    if not coffee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coffee menu item not found or not available"
        )
    return coffee

@router.post("/favorites/{coffee_id}", status_code=status.HTTP_201_CREATED)
async def add_to_favorites(
    coffee_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Add a coffee item to user's favorites"""
    success = coffee_menu_service.add_to_favorites(db, coffee_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to add to favorites. Item might already be in favorites or not found."
        )
    return {"detail": "Added to favorites successfully"}

@router.delete("/favorites/{coffee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_favorites(
    coffee_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Remove a coffee item from user's favorites"""
    success = coffee_menu_service.remove_from_favorites(db, coffee_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in favorites"
        )
    return {"detail": "Removed from favorites successfully"}

@router.get("/favorites", response_model=List[CoffeeMenuPublicResponse])
async def get_favorites(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get all favorite coffee items for the current user"""
    return coffee_menu_service.get_favorites(db, current_user.id)