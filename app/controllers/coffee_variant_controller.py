from typing import List, Optional
from uuid import UUID
from app.schemas.coffee_schema import CoffeeVariantCreate, CoffeeVariantResponse
from app.services.coffee_variant_service import CoffeeVariantService

class CoffeeVariantController:
    def __init__(self, db):
        self.service = CoffeeVariantService(db)
    
    def create_coffee_variant(self, coffee_variant: CoffeeVariantCreate):
        return self.service.create_coffee_variant(coffee_variant)
    
    def get_coffee_variants(self, coffee_id: Optional[UUID] = None, variant_id: Optional[UUID] = None):
        return self.service.get_coffee_variants(coffee_id, variant_id)
    
    def delete_coffee_variant(self, coffee_variant_id: UUID):
        self.service.delete_coffee_variant(coffee_variant_id)