from fastapi import APIRouter, Depends, status
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.controllers.coffee_variant_controller import CoffeeVariantController
from app.schemas.coffee_schema import CoffeeVariantCreate, CoffeeVariantResponse
from app.core.database import get_db
from app.utils.security import get_current_admin_user

router = APIRouter()


@router.post("/coffee-variants", response_model=CoffeeVariantResponse, status_code=status.HTTP_201_CREATED)
def create_coffee_variant(
    coffee_variant: CoffeeVariantCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Connect a coffee menu item with a variant (Admin only)"""
    controller = CoffeeVariantController(db)
    return controller.create_coffee_variant(coffee_variant)

@router.get("/coffee-variants", response_model=List[CoffeeVariantResponse])
def get_coffee_variants(
    coffee_id: Optional[UUID] = None,
    variant_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    # current_user: dict = Depends(get_current_admin_user)
):
    """Get all coffee-variant connections (Admin only)"""
    controller = CoffeeVariantController(db)
    return controller.get_coffee_variants(coffee_id, variant_id)

@router.delete("/coffee-variants/{coffee_variant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_coffee_variant(
    coffee_variant_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Remove a connection between a coffee menu item and a variant (Admin only)"""
    controller = CoffeeVariantController(db)
    controller.delete_coffee_variant(coffee_variant_id)
    return None