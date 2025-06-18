from typing import Dict, List, Optional
from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime

# ==================== Coffee Menu Schemas ====================

class CoffeeMenuBase(BaseModel):
    """Base schema for coffee menu items"""
    name: str
    price: int
    description: Optional[str] = None
    image_url: Optional[str] = None  # This remains Optional[str] for the stored URL/path
    is_available: bool = True

    long_description: Optional[str] = None 
    category: Optional[str] = None      # Kategori (e.g., 'Coffee', 'Non-Coffee', 'Iced')
    tags: Optional[List[str]] = None    # Tag (e.g., ['strong', 'classic'])
    preparation_time: Optional[str] = None # Waktu persiapan
    caffeine_content: Optional[str] = None # Kandungan kafein
    origin: Optional[str] = None        # Asal biji kopi
    roast_level: Optional[str] = None   # Tingkat roasting

class CoffeeMenuCreate(CoffeeMenuBase):
    """Schema for creating a coffee menu item"""
    coffee_shop_id: UUID

class CoffeeMenuUpdate(BaseModel):
    """Schema for updating a coffee menu item"""
    name: Optional[str] = None
    price: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None  # Allows updating to a new URL or explicitly setting to None
    is_available: Optional[bool] = None
    coffee_shop_id: Optional[UUID] = None # Allowing to change coffee shop if needed

    long_description: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    preparation_time: Optional[str] = None
    caffeine_content: Optional[str] = None
    origin: Optional[str] = None
    roast_level: Optional[str] = None

class CoffeeMenuResponse(CoffeeMenuBase):
    """Schema for coffee menu item response"""
    id: UUID
    coffee_shop_id: UUID
    average_rating: Optional[float] = None 
    total_ratings: int = 0               
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ==================== Variant Type Schemas ====================

class VariantTypeBase(BaseModel):
    """Base schema for variant types"""
    name: str
    description: Optional[str] = None
    is_required: bool = False

class VariantTypeCreate(VariantTypeBase):
    """Schema for creating a variant type"""
    pass

class VariantTypeUpdate(BaseModel):
    """Schema for updating a variant type"""
    name: Optional[str] = None
    description: Optional[str] = None
    is_required: Optional[bool] = None

class VariantTypeResponse(VariantTypeBase):
    """Schema for variant type response"""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ==================== Variant Schemas ====================

class VariantBase(BaseModel):
    """Base schema for variants"""
    name: str
    additional_price: int = 0
    is_available: bool = True

class VariantCreate(VariantBase):
    """Schema for creating a variant"""
    variant_type_id: UUID

class VariantUpdate(BaseModel):
    """Schema for updating a variant"""
    name: Optional[str] = None
    additional_price: Optional[int] = None
    is_available: Optional[bool] = None
    variant_type_id: Optional[UUID] = None

class VariantResponse(VariantBase):
    """Schema for variant response"""
    id: UUID
    variant_type_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ==================== Coffee Variant Schemas ====================

class CoffeeVariantBase(BaseModel):
    """Base schema for coffee variants"""
    is_default: bool = False

class CoffeeVariantCreate(CoffeeVariantBase):
    """Schema for creating a coffee variant"""
    coffee_id: UUID
    variant_id: UUID

class CoffeeVariantResponse(CoffeeVariantBase):
    """Schema for coffee variant response"""
    id: UUID
    coffee_id: UUID
    variant_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ==================== Public Coffee Menu Schemas ====================

class CoffeeVariantDetail(BaseModel):
    """Schema for variant details in public responses"""
    id: UUID
    name: str
    additional_price: int
    is_available: bool
    is_default: bool
    variant_type_id: UUID
    variant_type_name: str
    is_required: bool

    class Config:
        from_attributes = True

class CoffeeMenuPublicResponse(BaseModel):
    """Schema for public coffee menu item response (untuk daftar menu)"""
    id: UUID
    name: str
    price: int
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_available: bool = True
    rating_average: Optional[float] = None
    rating_count: int = 0
    is_favorite: bool = False
    coffee_shop_id: UUID
    coffee_shop_name: str
    
    # Kolom baru yang akan ditampilkan di menu publik
    category: Optional[str] = None # Untuk filter kategori
    tags: Optional[List[str]] = None # Untuk menampilkan tag di card

    class Config:
        from_attributes = True

class CoffeeMenuDetailResponse(CoffeeMenuPublicResponse):
    """Schema for detailed coffee menu item response"""
    # Tambahkan field detail produk
    long_description: Optional[str] = None
    preparation_time: Optional[str] = None
    caffeine_content: Optional[str] = None
    origin: Optional[str] = None
    roast_level: Optional[str] = None

    variants: Dict[str, List[CoffeeVariantDetail]] 

    class Config:
        from_attributes = True

class CoffeeFilter(BaseModel):
    """Schema for filtering coffee menu items"""
    min_price: Optional[int] = None
    max_price: Optional[int] = None
    search: Optional[str] = None
    sort_by: Optional[str] = "name"  # name, price, rating
    sort_order: Optional[str] = "asc"  # asc, desc
    rating: Optional[int] = None  # Minimum rating to filter by (1-5)
    category: Optional[str] = None # <--- Tambahkan filter kategori
    tags: Optional[List[str]] = None # <--- Tambahkan filter berdasarkan tags (akan butuh parsing dari query string)

class RatingCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    review: Optional[str] = None

# Skema baru untuk respons ulasan
class RatingResponse(BaseModel):
    id: UUID
    user_name: str # Nama user yang memberi ulasan
    rating: int
    review: Optional[str] = None
    created_at: datetime 

    class Config:
        from_attributes = True