from typing import List
from uuid import UUID
from fastapi import HTTPException, status
from app.schemas.coffee_schema import VariantTypeCreate, VariantTypeUpdate, VariantTypeResponse
from app.repositories.variant_type_repository import VariantTypeRepository

class VariantTypeService:
    def __init__(self, db):
        self.repository = VariantTypeRepository(db)
    
    def create_variant_type(self, variant_type: VariantTypeCreate):
        # Check if variant type with the same name already exists
        if self.repository.get_variant_type_by_name(variant_type.name):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Variant type with name '{variant_type.name}' already exists"
            )
            
        # Create new variant type
        return self.repository.create_variant_type(variant_type)
    
    def get_variant_types(self, skip: int = 0, limit: int = 100):
        return self.repository.get_variant_types(skip, limit)
    
    def get_variant_type_by_id(self, variant_type_id: UUID):
        variant_type = self.repository.get_variant_type_by_id(variant_type_id)
        if not variant_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Variant type with id {variant_type_id} not found"
            )
        return variant_type
    
    def update_variant_type(self, variant_type_id: UUID, variant_type: VariantTypeUpdate):
        db_variant_type = self.repository.get_variant_type_by_id(variant_type_id)
        if not db_variant_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Variant type with id {variant_type_id} not found"
            )
        
        # Check if updating name to an existing one
        if variant_type.name and variant_type.name != db_variant_type.name:
            existing = self.repository.get_variant_type_by_name(variant_type.name)
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Variant type with name '{variant_type.name}' already exists"
                )
        
        return self.repository.update_variant_type(variant_type_id, variant_type)
    
    def delete_variant_type(self, variant_type_id: UUID):
        variant_type = self.repository.get_variant_type_by_id(variant_type_id)
        if not variant_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Variant type with id {variant_type_id} not found"
            )
        
        # Check if variants exist for this variant type
        if self.repository.check_variants_exist(variant_type_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete variant type that has variants. Delete the variants first."
            )
        
        self.repository.delete_variant_type(variant_type_id)