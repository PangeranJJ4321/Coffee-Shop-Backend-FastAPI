from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from app.schemas.coffee_schema import CoffeeVariantCreate, CoffeeVariantResponse
from app.repositories.coffee_variant_repository import CoffeeVariantRepository

class CoffeeVariantService:
    def __init__(self, db):
        self.repository = CoffeeVariantRepository(db)
    
    def create_coffee_variant(self, coffee_variant: CoffeeVariantCreate):
        # Check if the coffee exists
        if not self.repository.get_coffee_by_id(coffee_variant.coffee_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Coffee menu with id {coffee_variant.coffee_id} not found"
            )
        
        # Check if the variant exists
        if not self.repository.get_variant_by_id(coffee_variant.variant_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Variant with id {coffee_variant.variant_id} not found"
            )
        
        # Check if connection already exists
        if self.repository.check_connection_exists(coffee_variant.coffee_id, coffee_variant.variant_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This coffee already has this variant connected"
            )
        
        # Create new coffee variant connection
        return self.repository.create_coffee_variant(coffee_variant)
    
    def get_coffee_variants(self, coffee_id: Optional[UUID] = None, variant_id: Optional[UUID] = None):
        return self.repository.get_coffee_variants(coffee_id, variant_id)
    
    def delete_coffee_variant(self, coffee_variant_id: UUID):
        coffee_variant = self.repository.get_coffee_variant_by_id(coffee_variant_id)
        if not coffee_variant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Coffee variant connection with id {coffee_variant_id} not found"
            )
        
        self.repository.delete_coffee_variant(coffee_variant_id)