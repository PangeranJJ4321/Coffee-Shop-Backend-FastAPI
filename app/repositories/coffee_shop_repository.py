# app/repositories/coffee_shop_repository.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.coffee import CoffeeShopModel
from app.schemas.coffe_shop_schema import CoffeeShopCreate, CoffeeShopUpdate

class CoffeeShopRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, coffee_shop_data: CoffeeShopCreate) -> CoffeeShopModel:
        db_coffee_shop = CoffeeShopModel(**coffee_shop_data.model_dump())
        self.db.add(db_coffee_shop)
        self.db.commit()
        self.db.refresh(db_coffee_shop)
        return db_coffee_shop

    def get_by_id(self, coffee_shop_id: UUID) -> Optional[CoffeeShopModel]:
        return self.db.query(CoffeeShopModel).filter(CoffeeShopModel.id == coffee_shop_id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[CoffeeShopModel]:
        return self.db.query(CoffeeShopModel).offset(skip).limit(limit).all()

    def update(self, coffee_shop: CoffeeShopModel, update_data: CoffeeShopUpdate) -> CoffeeShopModel:
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(coffee_shop, field, value)
        self.db.commit()
        self.db.refresh(coffee_shop)
        return coffee_shop

    def delete(self, coffee_shop: CoffeeShopModel):
        self.db.delete(coffee_shop)
        self.db.commit()
        return True