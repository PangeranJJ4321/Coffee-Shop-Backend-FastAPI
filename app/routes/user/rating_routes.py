from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import UserModel
from app.schemas.coffee_schema import RatingCreate, RatingResponse 
from app.services.coffee_menu_service import coffee_menu_service
from app.utils.security import get_current_user

router = APIRouter(prefix="/ratings", tags=["Coffee Ratings"])

@router.post("/coffee/{coffee_id}", status_code=status.HTTP_201_CREATED)
async def rate_coffee(
    coffee_id: UUID,
    rating: RatingCreate, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Rate a coffee item and optionally provide a review"""
    success = coffee_menu_service.add_rating(db, coffee_id, current_user.id, rating)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coffee menu item not found or not available"
        )
    return {"detail": "Rating submitted successfully"}

@router.get("/coffee/{coffee_id}", response_model=List[RatingResponse]) 
async def get_coffee_reviews(
    coffee_id: UUID,
    db: Session = Depends(get_db)
):
    """Get all reviews for a specific coffee item"""
    reviews = coffee_menu_service.get_coffee_reviews(db, coffee_id)
    if not reviews:
        return []
    return reviews