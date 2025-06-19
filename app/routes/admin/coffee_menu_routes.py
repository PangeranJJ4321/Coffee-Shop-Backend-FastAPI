# app/routes/admin/coffee_menu_routes.py
from fastapi import APIRouter, Depends, status, UploadFile, File, Form # Import File and Form
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.controllers.coffee_menu_controller import CoffeeMenuController
from app.schemas.coffee_schema import CoffeeMenuCreate, CoffeeMenuUpdate, CoffeeMenuResponse
from app.core.database import get_db
from app.utils.security import get_current_admin_user

router = APIRouter()

@router.post("/menu", response_model=CoffeeMenuResponse, status_code=status.HTTP_201_CREATED)
async def create_coffee_menu( # Make async
    name: str = Form(...), # Use Form for individual fields
    price: int = Form(...),
    description: Optional[str] = Form(None),
    is_available: bool = Form(True),
    coffee_shop_id: UUID = Form(...),
    image_file: Optional[UploadFile] = File(None), # Accept UploadFile
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Create a new coffee menu item (Admin only)"""
    coffee_menu_data = CoffeeMenuCreate(
        name=name,
        price=price,
        description=description,
        is_available=is_available,
        coffee_shop_id=coffee_shop_id
    )
    controller = CoffeeMenuController(db)
    return await controller.create_coffee_menu(coffee_menu_data, image_file) # Pass image_file

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
async def update_coffee_menu( # Make async
    coffee_id: UUID,
    name: Optional[str] = Form(None),
    price: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    featured: bool = Form(...),
    image_url: Optional[str] = Form(None), # Allow updating by URL directly or setting to None
    is_available: Optional[bool] = Form(None),
    coffee_shop_id: Optional[UUID] = Form(None),
    image_file: Optional[UploadFile] = File(None), # Accept new image file
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Update a coffee menu item (Admin only)"""
    update_data = CoffeeMenuUpdate(
        name=name,
        price=price,
        description=description,
        image_url=image_url, 
        featured=featured,
        is_available=is_available,
        coffee_shop_id=coffee_shop_id
    )
    controller = CoffeeMenuController(db)
    return await controller.update_coffee_menu(coffee_id, update_data, image_file) # Pass image_file

@router.delete("/menu/{coffee_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_coffee_menu( # Make async
    coffee_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Delete a coffee menu item (Admin only)"""
    controller = CoffeeMenuController(db)
    await controller.delete_coffee_menu(coffee_id) # Await the async call
    return None