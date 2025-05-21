from typing import List, Optional
from uuid import UUID
from app.schemas.coffee_schema import VariantCreate, VariantUpdate, VariantResponse
from app.services.variant_service import VariantService

class VariantController:
    def __init__(self, db):
        self.service = VariantService(db)
    
    def create_variant(self, variant: VariantCreate):
        return self.service.create_variant(variant)
    
    def get_variants(self, variant_type_id: Optional[UUID] = None, skip: int = 0, limit: int = 100):
        return self.service.get_variants(variant_type_id, skip, limit)
    
    def get_variant_by_id(self, variant_id: UUID):
        return self.service.get_variant_by_id(variant_id)
    
    def update_variant(self, variant_id: UUID, variant: VariantUpdate):
        return self.service.update_variant(variant_id, variant)
    
    def delete_variant(self, variant_id: UUID):
        self.service.delete_variant(variant_id)