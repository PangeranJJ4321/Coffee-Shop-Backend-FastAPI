from typing import List, Optional
from uuid import UUID
from app.models.coffee import CoffeeVariantModel,CoffeeMenuModel, VariantModel
from app.schemas.coffee_schema import CoffeeVariantCreate

class CoffeeVariantRepository:
    def __init__(self, db):
        self.db = db
    
    def get_coffee_by_id(self, coffee_id: UUID):
        return self.db.query(CoffeeMenuModel).filter(CoffeeMenuModel.id == coffee_id).first()
    
    def get_variant_by_id(self, variant_id: UUID):
        return self.db.query(VariantModel).filter(VariantModel.id == variant_id).first()
    
    def check_connection_exists(self, coffee_id: UUID, variant_id: UUID):
        return self.db.query(CoffeeVariantModel).filter(
            CoffeeVariantModel.coffee_id == coffee_id,
            CoffeeVariantModel.variant_id == variant_id
        ).first() is not None
    
    def create_coffee_variant(self, coffee_variant: CoffeeVariantCreate):
        new_coffee_variant = CoffeeVariantModel(
            coffee_id=coffee_variant.coffee_id,
            variant_id=coffee_variant.variant_id,
            is_default=coffee_variant.is_default
        )
        self.db.add(new_coffee_variant)
        self.db.commit()
        self.db.refresh(new_coffee_variant)
        return new_coffee_variant
    
    def get_coffee_variants(self, coffee_id: Optional[UUID] = None, variant_id: Optional[UUID] = None):
        query = self.db.query(CoffeeVariantModel)
        if coffee_id:
            query = query.filter(CoffeeVariantModel.coffee_id == coffee_id)
        if variant_id:
            query = query.filter(CoffeeVariantModel.variant_id == variant_id)
        return query.all()
    
    def get_coffee_variant_by_id(self, coffee_variant_id: UUID):
        return self.db.query(CoffeeVariantModel).filter(CoffeeVariantModel.id == coffee_variant_id).first()
    
    def delete_coffee_variant(self, coffee_variant_id: UUID):
        coffee_variant = self.get_coffee_variant_by_id(coffee_variant_id)
        self.db.delete(coffee_variant)
        self.db.commit()