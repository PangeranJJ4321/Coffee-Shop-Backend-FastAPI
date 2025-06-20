from typing import List
from uuid import UUID

from pytest import Session
from app.models.coffee import VariantTypeModel, VariantModel
from app.schemas.coffee_schema import VariantTypeCreate, VariantTypeUpdate

class VariantTypeRepository:
    def __init__(self, db: Session):
        self.db = db
        self.model = VariantTypeModel
    
    def create_variant_type(self, variant_type: VariantTypeCreate) -> VariantTypeModel: # Tambahkan tipe hint
        new_variant_type = self.model( 
            name=variant_type.name,
            description=variant_type.description,
            is_required=variant_type.is_required
        )
        self.db.add(new_variant_type)
        self.db.commit()
        self.db.refresh(new_variant_type)
        return new_variant_type

    def get_variant_type_by_name(self, name: str):
        return self.db.query(self.model).filter(self.model.name == name).first() # <-- Ubah ini
    
    def get_variant_types(self, skip: int = 0, limit: int = 100):
        return self.db.query(self.model).offset(skip).limit(limit).all() # <-- Ubah ini
    
    def get_variant_type_by_id(self, variant_type_id: UUID):
        return self.db.query(self.model).filter(self.model.id == variant_type_id).first() # <-- Ubah ini
    
    def update_variant_type(self, variant_type_id: UUID, variant_type: VariantTypeUpdate):
        db_variant_type = self.get_variant_type_by_id(variant_type_id)
        
        # Update variant type attributes
        update_data = variant_type.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_variant_type, key, value)
            
        self.db.commit()
        self.db.refresh(db_variant_type)
        return db_variant_type
    
    def delete_variant_type(self, variant_type_id: UUID):
        variant_type = self.get_variant_type_by_id(variant_type_id)
        self.db.delete(variant_type)
        self.db.commit()
    
    def check_variants_exist(self, variant_type_id: UUID):
        return self.db.query(VariantModel).filter(VariantModel.variant_type_id == variant_type_id).first() is not None