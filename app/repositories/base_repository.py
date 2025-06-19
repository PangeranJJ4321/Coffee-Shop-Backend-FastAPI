from typing import Generic, TypeVar, Type, List, Optional, Any, Dict, Union
from uuid import UUID
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base) # type: ignore
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base repository with common database operations
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db
    
    def get(self, id: UUID) -> Optional[ModelType]:
        """Get entity by ID"""
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_by_field(self, field_name: str, value: Any) -> Optional[ModelType]:
        """Get entity by a specific field value"""
        return self.db.query(self.model).filter(getattr(self.model, field_name) == value).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all entities with pagination"""
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def create(self, obj_in: Union[CreateSchemaType, Dict[str, Any]]) -> ModelType:
        """Create new entity"""
        self.db.add(obj_in) # Langsung tambahkan objek model SQLAlchemy ke session
        self.db.commit()
        self.db.refresh(obj_in) # Refresh untuk mendapatkan ID atau nilai default lainnya
        return obj_in
    
    def update(self, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        """Update entity"""
        obj_data = db_obj.__dict__.copy()
        
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
            
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
                
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
    
    def delete(self, id: UUID) -> bool:
        """Delete entity by ID"""
        db_obj = self.db.query(self.model).filter(self.model.id == id).first()
        if db_obj:
            self.db.delete(db_obj)
            self.db.commit()
            return True
        return False