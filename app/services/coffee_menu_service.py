from typing import List, Optional
from uuid import UUID
from fastapi import HTTPException, status
from app.schemas.coffee_schema import CoffeeMenuCreate, CoffeeMenuUpdate, CoffeeMenuResponse
from app.repositories.coffee_menu_repository import CoffeeMenuRepository

class CoffeeMenuService:
    def __init__(self, db):
        self.repository = CoffeeMenuRepository(db)
    
    def create_coffee_menu(self, coffee_menu: CoffeeMenuCreate):
        # Check if the coffee shop exists
        if not self.repository.get_coffee_shop_by_id(coffee_menu.coffee_shop_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Coffee shop with id {coffee_menu.coffee_shop_id} not found"
            )
            
        # Create new coffee menu item
        return self.repository.create_coffee_menu(coffee_menu)
    
    def get_coffee_menu(self, coffee_shop_id: Optional[UUID] = None, skip: int = 0, limit: int = 100):
        return self.repository.get_coffee_menu(coffee_shop_id, skip, limit)
    
    def get_coffee_menu_by_id(self, coffee_id: UUID):
        coffee = self.repository.get_coffee_menu_by_id(coffee_id)
        if not coffee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Coffee menu with id {coffee_id} not found"
            )
        return coffee
    
    def update_coffee_menu(self, coffee_id: UUID, coffee_menu: CoffeeMenuUpdate):
        coffee = self.repository.get_coffee_menu_by_id(coffee_id)
        if not coffee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Coffee menu with id {coffee_id} not found"
            )
        
        return self.repository.update_coffee_menu(coffee_id, coffee_menu)
    
    def delete_coffee_menu(self, coffee_id: UUID):
        coffee = self.repository.get_coffee_menu_by_id(coffee_id)
        if not coffee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Coffee menu with id {coffee_id} not found"
            )
        
        self.repository.delete_coffee_menu(coffee_id)