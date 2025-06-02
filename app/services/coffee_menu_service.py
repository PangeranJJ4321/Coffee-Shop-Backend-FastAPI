# app/services/coffee_menu_service.py
"""
Coffee menu service implementation
"""
import os
from typing import List, Optional, Dict
from uuid import UUID
from sqlalchemy import func, cast, Float
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
import re

# Import the new Supabase utility functions
from app.utils.supabase_file_handler import upload_file_to_supabase, delete_file_from_supabase

from app.models.coffee import CoffeeMenuModel, CoffeeShopModel, CoffeeVariantModel, VariantModel, VariantTypeModel
from app.models.notification import UserFavoriteModel, RatingModel
from app.schemas.coffee_schema import (
    CoffeeMenuCreate,
    CoffeeMenuUpdate,
    CoffeeMenuResponse,
    CoffeeMenuPublicResponse,
    CoffeeMenuDetailResponse,
    CoffeeFilter,
    CoffeeVariantDetail,
    RatingCreate
)

class CoffeeMenuService:
    def __init__(self, db):
        self.db = db

    async def create_coffee_menu(self, coffee_menu: CoffeeMenuCreate, image_file: Optional[UploadFile] = None) -> CoffeeMenuModel:
        """Create a new coffee menu item"""
        # Check if the coffee shop exists
        coffee_shop = self.db.query(CoffeeShopModel).filter(
            CoffeeShopModel.id == coffee_menu.coffee_shop_id
        ).first()

        if not coffee_shop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Coffee shop with id {coffee_menu.coffee_shop_id} not found"
            )

        processed_image_url = None
        if image_file:
            # Save the uploaded file to Supabase Storage and get its public URL
            image_url = await upload_file_to_supabase(image_file, subdirectory="coffee_menu_images")

        # Create new coffee menu item
        db_coffee_menu = CoffeeMenuModel(
            **coffee_menu.dict(exclude={"image_url"}), 
            image_url=processed_image_url 
        )
        self.db.add(db_coffee_menu)
        self.db.commit()
        self.db.refresh(db_coffee_menu)
        return db_coffee_menu

    def get_coffee_menu(self, coffee_shop_id: Optional[UUID] = None, skip: int = 0, limit: int = 100) -> List[CoffeeMenuModel]:
        """Get coffee menu items with optional filtering by coffee shop"""
        query = self.db.query(CoffeeMenuModel)

        if coffee_shop_id:
            query = query.filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)

        return query.offset(skip).limit(limit).all()

    def get_coffee_menu_by_id(self, coffee_id: UUID) -> CoffeeMenuModel:
        """Get a coffee menu item by ID"""
        coffee = self.db.query(CoffeeMenuModel).filter(CoffeeMenuModel.id == coffee_id).first()
        if not coffee:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Coffee menu with id {coffee_id} not found"
            )
        return coffee

    async def update_coffee_menu(self, coffee_id: UUID, coffee_menu: CoffeeMenuUpdate, image_file: Optional[UploadFile] = None) -> CoffeeMenuModel:
        """Update a coffee menu item"""
        coffee = self.get_coffee_menu_by_id(coffee_id)

        old_image_url = coffee.image_url # Store the old image URL

        update_data = coffee_menu.dict(exclude_unset=True)

        if image_file:
            # Upload new image to Supabase Storage
            new_image_url = await upload_file_to_supabase(image_file, subdirectory="coffee_menu_images")
            update_data["image_url"] = new_image_url
            # Delete old image from Supabase Storage if it was a Supabase URL
            if old_image_url and "/storage/v1/object/public/" in old_image_url: # Basic check for Supabase URL pattern
                await delete_file_from_supabase(old_image_url)
        elif "image_url" in update_data and update_data["image_url"] is None:
            # If image_url is explicitly set to None in the update payload
            if old_image_url and "/storage/v1/object/public/" in old_image_url:
                await delete_file_from_supabase(old_image_url)
            update_data["image_url"] = None # Ensure it's set to None in the DB


        for key, value in update_data.items():
            setattr(coffee, key, value)

        self.db.commit()
        self.db.refresh(coffee)
        return coffee

    async def delete_coffee_menu(self, coffee_id: UUID) -> None:
        """Delete a coffee menu item"""
        coffee = self.get_coffee_menu_by_id(coffee_id)
        if coffee.image_url and "/storage/v1/object/public/" in coffee.image_url:
            await delete_file_from_supabase(coffee.image_url) # Delete image from Supabase
        self.db.delete(coffee)
        self.db.commit()

    # The rest of the methods (get_public_menu, get_coffee_details, add_to_favorites, etc.)
    # remain the same as they only read the image_url string.
    def get_public_menu(
        self,
        db: Session,
        coffee_shop_id: UUID,
        filter_params: CoffeeFilter,
        current_user: Optional[any] = None
    ) -> List[CoffeeMenuPublicResponse]:
        """Get all available coffee menu items for public display with optional filtering"""
        from app.models.coffee import CoffeeShopModel

        # Check if coffee shop exists
        coffee_shop = db.query(CoffeeShopModel).filter(
            CoffeeShopModel.id == coffee_shop_id
        ).first()

        if not coffee_shop:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Coffee shop with id {coffee_shop_id} not found"
            )

        # Start with base query
        query = db.query(
            CoffeeMenuModel,
            func.avg(RatingModel.rating).label('avg_rating'),
            func.count(RatingModel.id).label('rating_count'),
            CoffeeShopModel.name.label('coffee_shop_name')
        ).join(
            CoffeeShopModel, CoffeeMenuModel.coffee_shop_id == CoffeeShopModel.id
        ).outerjoin(
            RatingModel, CoffeeMenuModel.id == RatingModel.coffee_id
        ).filter(
            CoffeeMenuModel.coffee_shop_id == coffee_shop_id,
            CoffeeMenuModel.is_available == True
        ).group_by(
            CoffeeMenuModel.id,
            CoffeeShopModel.name
        )

        # Apply filters
        if filter_params.min_price is not None:
            query = query.filter(CoffeeMenuModel.price >= filter_params.min_price)

        if filter_params.max_price is not None:
            query = query.filter(CoffeeMenuModel.price <= filter_params.max_price)

        if filter_params.search:
            search_term = f"%{filter_params.search}%"
            query = query.filter(CoffeeMenuModel.name.ilike(search_term) |
                                CoffeeMenuModel.description.ilike(search_term))

        if filter_params.rating:
            # Filter by having average rating >= specified rating
            query = query.having(func.avg(RatingModel.rating) >= filter_params.rating)

        # Apply sorting
        if filter_params.sort_by == "name":
            if filter_params.sort_order == "desc":
                query = query.order_by(CoffeeMenuModel.name.desc())
            else:
                query = query.order_by(CoffeeMenuModel.name.asc())
        elif filter_params.sort_by == "price":
            if filter_params.sort_order == "desc":
                query = query.order_by(CoffeeMenuModel.price.desc())
            else:
                query = query.order_by(CoffeeMenuModel.price.asc())
        elif filter_params.sort_by == "rating":
            if filter_params.sort_order == "desc":
                query = query.order_by(func.avg(RatingModel.rating).desc())
            else:
                query = query.order_by(func.avg(RatingModel.rating).asc())

        # Execute query
        results = query.all()

        # Get user favorites if user is authenticated
        user_favorites = set()
        if current_user:
            favorites = db.query(UserFavoriteModel).filter(
                UserFavoriteModel.user_id == current_user.id
            ).all()
            user_favorites = {fav.coffee_id for fav in favorites}

        # Prepare response
        coffee_items = []
        for item in results:
            coffee_menu = item[0]  # CoffeeMenuModel instance
            avg_rating = item[1]   # Average rating
            rating_count = item[2] # Rating count
            coffee_shop_name = item[3] # Coffee shop name

            # Create response object
            coffee_response = CoffeeMenuPublicResponse(
                id=coffee_menu.id,
                name=coffee_menu.name,
                price=coffee_menu.price,
                description=coffee_menu.description,
                image_url=coffee_menu.image_url,
                is_available=coffee_menu.is_available,
                rating_average=float(avg_rating) if avg_rating else None,
                rating_count=rating_count,
                is_favorite=coffee_menu.id in user_favorites,
                coffee_shop_id=coffee_menu.coffee_shop_id,
                coffee_shop_name=coffee_shop_name
            )
            coffee_items.append(coffee_response)

        return coffee_items

    def get_coffee_details(
        self,
        db: Session,
        coffee_id: UUID,
        current_user: Optional[any] = None
    ) -> CoffeeMenuDetailResponse:
        """Get detailed information about a specific coffee menu item"""
        from app.models.coffee import CoffeeShopModel

        # Query for coffee details with ratings
        coffee_query = db.query(
            CoffeeMenuModel,
            func.avg(RatingModel.rating).label('avg_rating'),
            func.count(RatingModel.id).label('rating_count'),
            CoffeeShopModel.name.label('coffee_shop_name')
        ).join(
            CoffeeShopModel, CoffeeMenuModel.coffee_shop_id == CoffeeShopModel.id
        ).outerjoin(
            RatingModel, CoffeeMenuModel.id == RatingModel.coffee_id
        ).filter(
            CoffeeMenuModel.id == coffee_id,
            CoffeeMenuModel.is_available == True
        ).group_by(
            CoffeeMenuModel.id,
            CoffeeShopModel.name
        ).first()

        if not coffee_query:
            return None

        coffee_menu = coffee_query[0]  # CoffeeMenuModel instance
        avg_rating = coffee_query[1]   # Average rating
        rating_count = coffee_query[2] # Rating count
        coffee_shop_name = coffee_query[3] # Coffee shop name

        # Check if it's a favorite
        is_favorite = False
        if current_user:
            favorite = db.query(UserFavoriteModel).filter(
                UserFavoriteModel.user_id == current_user.id,
                UserFavoriteModel.coffee_id == coffee_id
            ).first()
            is_favorite = favorite is not None

        # Get variants
        variants_query = db.query(
            CoffeeVariantModel,
            VariantModel,
            VariantTypeModel
        ).join(
            VariantModel, CoffeeVariantModel.variant_id == VariantModel.id
        ).join(
            VariantTypeModel, VariantModel.variant_type_id == VariantTypeModel.id
        ).filter(
            CoffeeVariantModel.coffee_id == coffee_id,
            VariantModel.is_available == True
        ).all()

        # Organize variants by type
        variants_by_type = {}
        for coffee_variant, variant, variant_type in variants_query:
            if variant_type.name not in variants_by_type:
                variants_by_type[variant_type.name] = []

            variant_detail = CoffeeVariantDetail(
                id=variant.id,
                name=variant.name,
                additional_price=variant.additional_price,
                is_available=variant.is_available,
                is_default=coffee_variant.is_default,
                variant_type_id=variant_type.id,
                variant_type_name=variant_type.name,
                is_required=variant_type.is_required
            )
            variants_by_type[variant_type.name].append(variant_detail)

        # Create response
        coffee_detail = CoffeeMenuDetailResponse(
            id=coffee_menu.id,
            name=coffee_menu.name,
            price=coffee_menu.price,
            description=coffee_menu.description,
            image_url=coffee_menu.image_url,
            is_available=coffee_menu.is_available,
            rating_average=float(avg_rating) if avg_rating else None,
            rating_count=rating_count,
            is_favorite=is_favorite,
            coffee_shop_id=coffee_menu.coffee_shop_id,
            coffee_shop_name=coffee_shop_name,
            variants=variants_by_type
        )

        return coffee_detail

    def add_to_favorites(self, db: Session, coffee_id: UUID, user_id: UUID) -> bool:
        """Add a coffee item to user's favorites"""
        # Check if coffee exists
        coffee = db.query(CoffeeMenuModel).filter(
            CoffeeMenuModel.id == coffee_id,
            CoffeeMenuModel.is_available == True
        ).first()

        if not coffee:
            return False

        # Check if already in favorites
        existing_favorite = db.query(UserFavoriteModel).filter(
            UserFavoriteModel.coffee_id == coffee_id,
            UserFavoriteModel.user_id == user_id
        ).first()

        if existing_favorite:
            return False

        # Add to favorites
        favorite = UserFavoriteModel(
            user_id=user_id,
            coffee_id=coffee_id
        )
        db.add(favorite)
        db.commit()

        return True

    def remove_from_favorites(self, db: Session, coffee_id: UUID, user_id: UUID) -> bool:
        """Remove a coffee item from user's favorites"""
        favorite = db.query(UserFavoriteModel).filter(
            UserFavoriteModel.coffee_id == coffee_id,
            UserFavoriteModel.user_id == user_id
        ).first()

        if not favorite:
            return False

        db.delete(favorite)
        db.commit()

        return True

    def get_favorites(self, db: Session, user_id: UUID) -> List[CoffeeMenuPublicResponse]:
        """Get all favorite coffee items for a user"""
        from app.models.coffee import CoffeeShopModel

        favorites = db.query(
            CoffeeMenuModel,
            func.avg(RatingModel.rating).label('avg_rating'),
            func.count(RatingModel.id).label('rating_count'),
            CoffeeShopModel.name.label('coffee_shop_name')
        ).join(
            UserFavoriteModel, CoffeeMenuModel.id == UserFavoriteModel.coffee_id
        ).join(
            CoffeeShopModel, CoffeeMenuModel.coffee_shop_id == CoffeeShopModel.id
        ).outerjoin(
            RatingModel, CoffeeMenuModel.id == RatingModel.coffee_id
        ).filter(
            UserFavoriteModel.user_id == user_id,
            CoffeeMenuModel.is_available == True
        ).group_by(
            CoffeeMenuModel.id,
            CoffeeShopModel.name
        ).all()

        # Prepare response
        favorite_items = []
        for item in favorites:
            coffee_menu = item[0]  # CoffeeMenuModel instance
            avg_rating = item[1]   # Average rating
            rating_count = item[2] # Rating count
            coffee_shop_name = item[3] # Coffee shop name

            # Create response object
            coffee_response = CoffeeMenuPublicResponse(
                id=coffee_menu.id,
                name=coffee_menu.name,
                price=coffee_menu.price,
                description=coffee_menu.description,
                image_url=coffee_menu.image_url,
                is_available=coffee_menu.is_available,
                rating_average=float(avg_rating) if avg_rating else None,
                rating_count=rating_count,
                is_favorite=True,  # It's a favorite since we're querying favorites
                coffee_shop_id=coffee_menu.coffee_shop_id,
                coffee_shop_name=coffee_shop_name
            )
            favorite_items.append(coffee_response)

        return favorite_items

    def add_rating(self, db: Session, coffee_id: UUID, user_id: UUID, rating: RatingCreate) -> bool:
        """Add or update rating for a coffee item"""
        # Check if coffee exists
        coffee = db.query(CoffeeMenuModel).filter(
            CoffeeMenuModel.id == coffee_id,
            CoffeeMenuModel.is_available == True
        ).first()

        if not coffee:
            return False

        # Check if user already rated this coffee
        existing_rating = db.query(RatingModel).filter(
            RatingModel.coffee_id == coffee_id,
            RatingModel.user_id == user_id
        ).first()

        if existing_rating:
            # Update existing rating
            existing_rating.rating = rating.rating
            existing_rating.review = rating.review
        else:
            # Create new rating
            new_rating = RatingModel(
                user_id=user_id,
                coffee_id=coffee_id,
                rating=rating.rating,
                review=rating.review
            )
            db.add(new_rating)

        db.commit()
        return True

# Create service instance to be used in routes
coffee_menu_service = CoffeeMenuService(None)