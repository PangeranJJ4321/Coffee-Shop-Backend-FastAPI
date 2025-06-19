# app/models/coffee.py - DIREVISI BERDASARKAN FILE ANDA
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Float, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY # Import ARRAY untuk tags
from sqlalchemy.orm import relationship

from app.models.base import BaseModel # BaseModel sudah memiliki id, created_at, updated_at

class CoffeeShopModel(BaseModel):
    """Coffee shop model"""
    __tablename__ = "coffee_shops"
    
    name = Column(String, unique=True, nullable=False) # Tambah unique=True untuk name
    address = Column(Text, nullable=False)
    phone_number = Column(String, nullable=True) # Set nullable=True jika phone_number boleh kosong
    image_url = Column(String, nullable=True)
    description = Column(String) # Default ini sudah nullable=True
    average_rating = Column(Float, default=0.0) # <--- TAMBAH KOLOM INI
    total_ratings = Column(Integer, default=0) # <--- TAMBAH KOLOM INI
    
    # Relationships
    # Sesuaikan back_populates dengan nama relationship di CoffeeMenuModel (yang akan kita ubah)
    coffee_menus = relationship("CoffeeMenuModel", back_populates="coffee_shop") # <-- Ganti menu_items jadi coffee_menus
    time_slots = relationship("TimeSlotModel", back_populates="coffee_shop")
    tables = relationship("TableModel", back_populates="coffee_shop")
    operating_hours = relationship("OperatingHoursModel", back_populates="coffee_shop")
    
    def __repr__(self):
        return f"<CoffeeShop {self.name}>"

class CoffeeMenuModel(BaseModel):
    """Coffee menu model"""
    __tablename__ = "coffee_menus" 

    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    is_available = Column(Boolean, default=True, nullable=False)
    
    # Field rating agregat (diperbarui oleh rating service)
    average_rating = Column(Float, default=0.0) 
    total_ratings = Column(Integer, default=0) 

    # Kolom baru yang diminta frontend
    long_description = Column(Text, nullable=True) # Deskripsi lebih panjang
    category = Column(String, nullable=True, index=True) # Kategori (e.g., 'Coffee', 'Non-Coffee', 'Iced')
    tags = Column(ARRAY(String), nullable=True) # Tag (e.g., ['strong', 'classic'])
    preparation_time = Column(String, nullable=True) # Waktu persiapan (e.g., '3-5 menit')
    caffeine_content = Column(String, nullable=True) # Kandungan kafein (e.g., 'Tinggi', 'Rendah')
    origin = Column(String, nullable=True) # Asal biji kopi (e.g., 'Jawa Barat')
    roast_level = Column(String, nullable=True) 
    featured = Column(Boolean, default=False, nullable=False) # Menandai
    # Foreign keys
    coffee_shop_id = Column(UUID(as_uuid=True), ForeignKey("coffee_shops.id"), nullable=False)
    
    # Relationships
    coffee_shop = relationship("CoffeeShopModel", back_populates="coffee_menus") 
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
    coffee_id = Column(UUID(as_uuid=True), ForeignKey("coffee_menus.id"), nullable=False) # <--- Ubah foreign key
    variant_id = Column(UUID(as_uuid=True), ForeignKey("variants.id"), nullable=False)
    
    # Relationships
    coffee = relationship("CoffeeMenuModel", back_populates="coffee_variants")
    variant = relationship("VariantModel", back_populates="coffee_variants")
    
    def __repr__(self):
        return f"<CoffeeVariant {self.coffee_id}:{self.variant_id}>"