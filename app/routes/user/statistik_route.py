"""
Routes for user statistics and profile information
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import UserModel
from app.services.order_service import order_service
from app.utils.security import get_current_user

router = APIRouter(prefix="/user", tags=["User Profile"])

@router.get("/statistics")
async def get_user_statistics(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get user order statistics including pay for others data"""
    stats = order_service.get_order_statistics(db, current_user.id)
    
    return {
        "user_id": current_user.id,
        "user_name": current_user.name,
        "statistics": stats
    }
