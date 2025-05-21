from fastapi import APIRouter, Depends, status
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from app.controllers.variant_type_controller import VariantTypeController
from app.schemas.coffee_schema import VariantTypeCreate, VariantTypeUpdate, VariantTypeResponse
from app.core.database import get_db
from app.utils.security import get_current_admin_user

router = APIRouter()

@router.post("/variant-types", response_model=VariantTypeResponse, status_code=status.HTTP_201_CREATED)
def create_variant_type(
    variant_type: VariantTypeCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Create a new variant type (e.g., Size, Sugar Level) (Admin only)"""
    controller = VariantTypeController(db)
    return controller.create_variant_type(variant_type)

@router.get("/variant-types", response_model=List[VariantTypeResponse])
def get_variant_types(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get all variant types (Admin only)"""
    controller = VariantTypeController(db)
    return controller.get_variant_types(skip, limit)
 
@router.get("/variant-types/{variant_type_id}", response_model=VariantTypeResponse)
def get_variant_type_by_id(
    variant_type_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Get a variant type by ID (Admin only)"""
    controller = VariantTypeController(db)
    return controller.get_variant_type_by_id(variant_type_id)

@router.put("/variant-types/{variant_type_id}", response_model=VariantTypeResponse)
def update_variant_type(
    variant_type_id: UUID,
    variant_type: VariantTypeUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Update a variant type (Admin only)"""
    controller = VariantTypeController(db)
    return controller.update_variant_type(variant_type_id, variant_type)

@router.delete("/variant-types/{variant_type_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_variant_type(
    variant_type_id: UUID,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_admin_user)
):
    """Delete a variant type (Admin only)"""
    controller = VariantTypeController(db)
    controller.delete_variant_type(variant_type_id)
    return None