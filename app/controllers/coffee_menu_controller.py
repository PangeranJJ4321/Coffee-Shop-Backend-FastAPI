from typing import List, Optional
from uuid import UUID
from app.services.coffee_menu_service import CoffeeMenuService
from app.schemas.coffee_schema import CoffeeMenuCreate, CoffeeMenuUpdate, CoffeeMenuResponse

class CoffeeMenuController:
    def __init__(self, db):
        self.service = CoffeeMenuService(db)
    
    def create_coffee_menu(self, coffee_menu: CoffeeMenuCreate):
        return self.service.create_coffee_menu(coffee_menu)
    
    def get_coffee_menu(self, coffee_shop_id: Optional[UUID] = None, skip: int = 0, limit: int = 100):
        return self.service.get_coffee_menu(coffee_shop_id, skip, limit)
    
    def get_coffee_menu_by_id(self, coffee_id: UUID):
        return self.service.get_coffee_menu_by_id(coffee_id)
    
    def update_coffee_menu(self, coffee_id: UUID, coffee_menu: CoffeeMenuUpdate):
        return self.service.update_coffee_menu(coffee_id, coffee_menu)
    
    def delete_coffee_menu(self, coffee_id: UUID):
        self.service.delete_coffee_menu(coffee_id)