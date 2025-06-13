# app/services/coffee_shop_service.py
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.database import get_db 
from app.models.coffee import CoffeeShopModel
from app.repositories.coffee_shop_repository import CoffeeShopRepository
from app.schemas.coffe_shop_schema import CoffeeShopCreate, CoffeeShopUpdate

class CoffeeShopService:
    def __init__(self, db: Session):
        self.db = db
        self.coffee_shop_repo = CoffeeShopRepository(db)

    def create_coffee_shop(self, coffee_shop_data: CoffeeShopCreate) -> CoffeeShopModel:
        existing_coffee_shop = self.db.query(CoffeeShopModel).filter(CoffeeShopModel.name == coffee_shop_data.name).first()
        if existing_coffee_shop:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Coffee shop with this name already exists"
            )
        return self.coffee_shop_repo.create(coffee_shop_data)

    def get_all_coffee_shops(self, skip: int = 0, limit: int = 100) -> List[CoffeeShopModel]:
        return self.coffee_shop_repo.get_all(skip, limit)

    def get_coffee_shop_by_id(self, coffee_shop_id: UUID) -> Optional[CoffeeShopModel]:
        coffee_shop = self.coffee_shop_repo.get_by_id(coffee_shop_id)
        if not coffee_shop:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coffee shop not found")
        return coffee_shop

    def update_coffee_shop(self, coffee_shop_id: UUID, update_data: CoffeeShopUpdate) -> CoffeeShopModel:
        coffee_shop = self.get_coffee_shop_by_id(coffee_shop_id)
        return self.coffee_shop_repo.update(coffee_shop, update_data)

    def delete_coffee_shop(self, coffee_shop_id: UUID) -> bool:
        coffee_shop = self.get_coffee_shop_by_id(coffee_shop_id)
        self.coffee_shop_repo.delete(coffee_shop)
        return True
