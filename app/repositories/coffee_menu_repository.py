from typing import List, Optional
from uuid import UUID
from app.models.coffee import CoffeeMenuModel, CoffeeShopModel
from app.schemas.coffee_schema import CoffeeMenuCreate, CoffeeMenuUpdate

class CoffeeMenuRepository:
    def __init__(self, db):
        self.db = db
    
    def get_coffee_shop_by_id(self, coffee_shop_id: UUID):
        return self.db.query(CoffeeShopModel).filter(CoffeeShopModel.id == coffee_shop_id).first()
    
    def create_coffee_menu(self, coffee_menu: CoffeeMenuCreate):
        new_coffee = CoffeeMenuModel(
            name=coffee_menu.name,
            price=coffee_menu.price,
            description=coffee_menu.description,
            image_url=coffee_menu.image_url,
            is_available=coffee_menu.is_available,
            coffee_shop_id=coffee_menu.coffee_shop_id
        )
        self.db.add(new_coffee)
        self.db.commit()
        self.db.refresh(new_coffee)
        return new_coffee
    
    def get_coffee_menu(self, coffee_shop_id: Optional[UUID] = None, skip: int = 0, limit: int = 100):
        query = self.db.query(CoffeeMenuModel)
        if coffee_shop_id:
            query = query.filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)
        return query.offset(skip).limit(limit).all()
    
    def get_coffee_menu_by_id(self, coffee_id: UUID):
        return self.db.query(CoffeeMenuModel).filter(CoffeeMenuModel.id == coffee_id).first()
    
    def update_coffee_menu(self, coffee_id: UUID, coffee_menu: CoffeeMenuUpdate):
        coffee = self.get_coffee_menu_by_id(coffee_id)
        
        # Update coffee menu attributes
        update_data = coffee_menu.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(coffee, key, value)
            
        self.db.commit()
        self.db.refresh(coffee)
        return coffee
    
    def delete_coffee_menu(self, coffee_id: UUID):
        coffee = self.get_coffee_menu_by_id(coffee_id)
        self.db.delete(coffee)
        self.db.commit()