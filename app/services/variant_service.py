from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from app.schemas.coffee_schema import VariantCreate, VariantUpdate, VariantResponse
from app.repositories.variant_repository import VariantRepository
from sqlalchemy.orm import joinedload
class VariantService:
    def __init__(self, db):
        self.repository = VariantRepository(db)
    
    def create_variant(self, variant: VariantCreate):
        # Check if the variant type exists
        if not self.repository.get_variant_type_by_id(variant.variant_type_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Variant type with id {variant.variant_type_id} not found"
            )
        
        # Create new variant
        return self.repository.create_variant(variant)
    
    def get_variants(self, variant_type_id: Optional[UUID] = None, skip: int = 0, limit: int = 100):
        query = self.repository.db.query(self.repository.model).options(
            joinedload(self.repository.model.variant_type)
        )

        if variant_type_id:
            query = query.filter(self.repository.model.variant_type_id == variant_type_id)

        variants = query.offset(skip).limit(limit).all()

        for variant in variants:
            if variant.variant_type:
                variant.variant_type_name = variant.variant_type.name 
            else:
                variant.variant_type_name = "Unknown Type"

        return variants
    
    def get_variant_by_id(self, variant_id: UUID):
        variant = self.repository.get_variant_by_id(variant_id)
        if not variant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Variant with id {variant_id} not found"
            )
        # Enrich for single variant detail
        if variant.variant_type:
            variant.variant_type_name = variant.variant_type.name
        else:
            variant.variant_type_name = "Unknown Type"
        return variant
    
    def update_variant(self, variant_id: UUID, variant: VariantUpdate):
        db_variant = self.repository.get_variant_by_id(variant_id)
        if not db_variant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Variant with id {variant_id} not found"
            )
        
        return self.repository.update_variant(variant_id, variant)
    
    def delete_variant(self, variant_id: UUID):
        variant = self.repository.get_variant_by_id(variant_id)
        if not variant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Variant with id {variant_id} not found"
            )
        
        # Check if coffee variants exist for this variant
        if self.repository.check_coffee_variant_exists(variant_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete variant that is connected to coffee menu items. Remove the connections first."
            )
        
        self.repository.delete_variant(variant_id)