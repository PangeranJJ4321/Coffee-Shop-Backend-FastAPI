from fastapi import APIRouter, Depends, status
from typing import List, Optional
from uuid import UUID
from app.controllers.variant_controller import VariantController
from app.schemas.coffee_schema import VariantCreate, VariantUpdate, VariantResponse
from app.core.database import get_db
from app.utils.security import get_current_admin_user
from sqlalchemy.orm import Session

router = APIRouter()


@router.post("/variants", response_model=VariantResponse, status_code=status.HTTP_201_CREATED)
def create_variant(
    variant: VariantCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Create a new variant (e.g., Small, Medium, Large) (Admin only)"""
    controller = VariantController(db)
    return controller.create_variant(variant)

@router.get("/variants", response_model=List[VariantResponse])
def get_variants(
    variant_type_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get all variants (Admin only)"""
    controller = VariantController(db)
    return controller.get_variants(variant_type_id, skip, limit)

@router.get("/variants/{variant_id}", response_model=VariantResponse)
def get_variant_by_id(
    variant_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get a variant by ID (Admin only)"""
    controller = VariantController(db)
    return controller.get_variant_by_id(variant_id)

@router.put("/variants/{variant_id}", response_model=VariantResponse)
def update_variant(
    variant_id: UUID,
    variant: VariantUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Update a variant (Admin only)"""
    controller = VariantController(db)
    return controller.update_variant(variant_id, variant)

@router.delete("/variants/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_variant(
    variant_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Delete a variant (Admin only)"""
    controller = VariantController(db)
    controller.delete_variant(variant_id)
    return None