from typing import List, Optional
from uuid import UUID

from pytest import Session
from app.models.coffee import VariantModel, VariantTypeModel, CoffeeVariantModel
from app.schemas.coffee_schema import VariantCreate, VariantUpdate

class VariantRepository:
    def __init__(self, db: Session):
        self.db = db
        self.model = VariantModel
    
    def get_variant_type_by_id(self, variant_type_id: UUID):
        return self.db.query(VariantTypeModel).filter(VariantTypeModel.id == variant_type_id).first()
    
    def create_variant(self, variant: VariantCreate) -> VariantModel:
        new_variant = self.model( 
            name=variant.name,
            additional_price=variant.additional_price,
            is_available=variant.is_available,
            variant_type_id=variant.variant_type_id
        )
        self.db.add(new_variant)
        self.db.commit()
        self.db.refresh(new_variant)
        return new_variant
    
    def get_variants(self, variant_type_id: Optional[UUID] = None, skip: int = 0, limit: int = 100):
        query = self.db.query(self.model) 
        if variant_type_id:
            query = query.filter(self.model.variant_type_id == variant_type_id) # <-- Ubah ini
        return query.offset(skip).limit(limit).all()
    
    def get_variant_by_id(self, variant_id: UUID):
        return self.db.query(self.model).filter(self.model.id == variant_id).first() # <-- Ubah ini

    def update_variant(self, variant_id: UUID, variant: VariantUpdate):
        db_variant = self.get_variant_by_id(variant_id)
        
        # Update variant attributes
        update_data = variant.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_variant, key, value)
        
        self.db.commit()
        self.db.refresh(db_variant)
        return db_variant
    
    def delete_variant(self, variant_id: UUID):
        variant = self.get_variant_by_id(variant_id)
        self.db.delete(variant)
        self.db.commit()
    
    def check_coffee_variant_exists(self, variant_id: UUID):
        return self.db.query(CoffeeVariantModel).filter(CoffeeVariantModel.variant_id == variant_id).first() is not None