from typing import List
from uuid import UUID
from app.services.variant_type_service import VariantTypeService
from app.schemas.coffee_schema import VariantTypeCreate, VariantTypeUpdate, VariantTypeResponse

class VariantTypeController:
    def __init__(self, db):
        self.service = VariantTypeService(db)
    
    def create_variant_type(self, variant_type: VariantTypeCreate):
        return self.service.create_variant_type(variant_type)
    
    def get_variant_types(self, skip: int = 0, limit: int = 100):
        return self.service.get_variant_types(skip, limit)
    
    def get_variant_type_by_id(self, variant_type_id: UUID):
        return self.service.get_variant_type_by_id(variant_type_id)
    
    def update_variant_type(self, variant_type_id: UUID, variant_type: VariantTypeUpdate):
        return self.service.update_variant_type(variant_type_id, variant_type)
    
    def delete_variant_type(self, variant_type_id: UUID):
        self.service.delete_variant_type(variant_type_id)