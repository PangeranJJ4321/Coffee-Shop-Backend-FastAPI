"""
Coffee shop and menu models
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class CoffeeShopModel(BaseModel):
    """Coffee shop model"""
    __tablename__ = "coffee_shops"
    
    name = Column(String, nullable=False)
    address = Column(Text, nullable=False)
    phone_number = Column(String, nullable=False)
    image_url = Column(String, nullable=True)
    
    # Relationships
    menu_items = relationship("CoffeeMenuModel", back_populates="coffee_shop")
    tables = relationship("TableModel", back_populates="coffee_shop")
    
    def __repr__(self):
        return f"<CoffeeShop {self.name}>"

class CoffeeMenuModel(BaseModel):
    """Coffee menu model"""
    __tablename__ = "coffee_menu"
    
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    is_available = Column(Boolean, default=True, nullable=False)
    
    # Foreign keys
    coffee_shop_id = Column(UUID(as_uuid=True), ForeignKey("coffee_shops.id"), nullable=False)
    
    # Relationships
    coffee_shop = relationship("CoffeeShopModel", back_populates="menu_items")
    coffee_variants = relationship("CoffeeVariantModel", back_populates="coffee")
    order_items = relationship("OrderItemModel", back_populates="coffee")
    favorites = relationship("UserFavoriteModel", back_populates="coffee")
    ratings = relationship("RatingModel", back_populates="coffee")
    
    def __repr__(self):
        return f"<CoffeeMenu {self.name}>"

class VariantTypeModel(BaseModel):
    """Variant type model (e.g., Size, Sugar Level, Milk Type)"""
    __tablename__ = "variant_types"
    
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=True)
    is_required = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    variants = relationship("VariantModel", back_populates="variant_type")
    
    def __repr__(self):
        return f"<VariantType {self.name}>"

class VariantModel(BaseModel):
    """Variant model (e.g., Small, Medium, Large)"""
    __tablename__ = "variants"
    
    name = Column(String, nullable=False)
    additional_price = Column(Integer, default=0, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    
    # Foreign keys
    variant_type_id = Column(UUID(as_uuid=True), ForeignKey("variant_types.id"), nullable=False)
    
    # Relationships
    variant_type = relationship("VariantTypeModel", back_populates="variants")
    coffee_variants = relationship("CoffeeVariantModel", back_populates="variant")
    order_item_variants = relationship("OrderItemVariantModel", back_populates="variant")
    
    def __repr__(self):
        return f"<Variant {self.name}>"

class CoffeeVariantModel(BaseModel):
    """Coffee variant model (connecting coffee with its available variants)"""
    __tablename__ = "coffee_variants"
    
    is_default = Column(Boolean, default=False, nullable=False)
    
    # Foreign keys
    coffee_id = Column(UUID(as_uuid=True), ForeignKey("coffee_menu.id"), nullable=False)
    variant_id = Column(UUID(as_uuid=True), ForeignKey("variants.id"), nullable=False)
    
    # Relationships
    coffee = relationship("CoffeeMenuModel", back_populates="coffee_variants")
    variant = relationship("VariantModel", back_populates="coffee_variants")
    
    def __repr__(self):
        return f"<CoffeeVariant {self.coffee_id}:{self.variant_id}>"