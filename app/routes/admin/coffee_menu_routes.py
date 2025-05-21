from fastapi import APIRouter, Depends, status
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.controllers.coffee_menu_controller import CoffeeMenuController
from app.schemas.coffee_schema import CoffeeMenuCreate, CoffeeMenuUpdate, CoffeeMenuResponse
from app.core.database import get_db 
from app.utils.security import get_current_admin_user

router = APIRouter()

@router.post("/menu", response_model=CoffeeMenuResponse, status_code=status.HTTP_201_CREATED)
def create_coffee_menu(
    coffee_menu: CoffeeMenuCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Create a new coffee menu item (Admin only)"""
    controller = CoffeeMenuController(db)
    return controller.create_coffee_menu(coffee_menu)

@router.get("/menu", response_model=List[CoffeeMenuResponse])
def get_coffee_menu(
    coffee_shop_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get all coffee menu items (Admin only)"""
    controller = CoffeeMenuController(db)
    return controller.get_coffee_menu(coffee_shop_id, skip, limit)

@router.get("/menu/{coffee_id}", response_model=CoffeeMenuResponse)
def get_coffee_menu_by_id(
    coffee_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get a coffee menu item by ID (Admin only)"""
    controller = CoffeeMenuController(db)
    return controller.get_coffee_menu_by_id(coffee_id)

@router.put("/menu/{coffee_id}", response_model=CoffeeMenuResponse)
def update_coffee_menu(
    coffee_id: UUID,
    coffee_menu: CoffeeMenuUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Update a coffee menu item (Admin only)"""
    controller = CoffeeMenuController(db)
    return controller.update_coffee_menu(coffee_id, coffee_menu)

@router.delete("/menu/{coffee_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_coffee_menu(
    coffee_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Delete a coffee menu item (Admin only)"""
    controller = CoffeeMenuController(db)
    controller.delete_coffee_menu(coffee_id)
    return None