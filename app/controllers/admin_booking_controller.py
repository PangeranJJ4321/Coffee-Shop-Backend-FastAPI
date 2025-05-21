"""
Controller for booking management
"""
from datetime import date
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import UserModel
from app.schemas.operating_hours_schema import TimeSlot, OperatingHours
from app.services.operating_hours_service import operating_hours_service, time_slot_service
from app.utils.security import get_current_user

router = APIRouter()

@router.get("/coffee-shops/{coffee_shop_id}/available-slots", response_model=List[TimeSlot])
async def get_available_time_slots(
    coffee_shop_id: UUID,
    date: date = Query(..., description="The date for which to get available slots"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get available time slots for a specific date"""
    # Get the day of the week for the date
    day_of_week = date.strftime("%A").upper()
    
    # Get operating hours for the day
    operating_hours = operating_hours_service.get_all_for_coffee_shop(db, coffee_shop_id)
    today_hours = next((oh for oh in operating_hours if oh.day.value == day_of_week), None)
    
    if not today_hours or not today_hours.is_open:
        return []  # Coffee shop is closed on this day
    
    time_slots = time_slot_service.get_all_for_coffee_shop(
        db, coffee_shop_id, active_only=True
    )
    
    available_slots = [
        slot for slot in time_slots 
        if slot.start_time >= today_hours.opening_time and 
        slot.end_time <= today_hours.closing_time
    ]
    
    return available_slots

@router.get("/coffee-shops/{coffee_shop_id}/operating-hours", response_model=List[OperatingHours])
async def get_coffee_shop_public_operating_hours(
    coffee_shop_id: UUID,
    db: Session = Depends(get_db)
):
    return operating_hours_service.get_all_for_coffee_shop(db, coffee_shop_id)