"""
Controller for admin booking management
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import UserModel
from app.schemas.operating_hours_schema import (
    OperatingHours, 
    OperatingHoursCreate, 
    OperatingHoursUpdate,
    TimeSlot,
    TimeSlotCreate,
    TimeSlotUpdate,
    BatchOperatingHoursUpdate,
    BatchTimeSlotUpdate
)
from app.services.operating_hours_service import operating_hours_service, time_slot_service
from app.utils.security import get_current_admin_user

router = APIRouter(prefix="/booking-management", tags=["Admin ~ Booking  Management"])

# Operating Hours Endpoints
@router.post("/operating-hours", response_model=OperatingHours)
async def create_operating_hours(
    operating_hours: OperatingHoursCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Create new operating hours for a coffee shop"""
    return operating_hours_service.create_operating_hours(db, operating_hours)

@router.get("/coffee-shops/{coffee_shop_id}/operating-hours", response_model=List[OperatingHours])
async def get_coffee_shop_operating_hours(
    coffee_shop_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get all operating hours for a coffee shop"""
    return operating_hours_service.get_all_for_coffee_shop(db, coffee_shop_id)

@router.put("/operating-hours/{operating_hours_id}", response_model=OperatingHours)
async def update_operating_hours(
    operating_hours_id: UUID,
    operating_hours_data: OperatingHoursUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Update operating hours"""
    operating_hours = operating_hours_service.update_operating_hours(
        db, operating_hours_id, operating_hours_data
    )
    if not operating_hours:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operating hours not found"
        )
    return operating_hours

@router.delete("/operating-hours/{operating_hours_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_operating_hours(
    operating_hours_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Delete operating hours"""
    success = operating_hours_service.delete_operating_hours(db, operating_hours_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Operating hours not found"
        )
    return {"detail": "Operating hours deleted successfully"}

@router.put("/coffee-shops/{coffee_shop_id}/operating-hours", response_model=List[OperatingHours])
async def batch_update_operating_hours(
    coffee_shop_id: UUID,
    operating_hours_data: BatchOperatingHoursUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Batch update operating hours for a coffee shop"""
    return operating_hours_service.batch_update_operating_hours(
        db, coffee_shop_id, operating_hours_data.operating_hours
    )

# Time Slot Endpoints
@router.post("/time-slots", response_model=TimeSlot)
async def create_time_slot(
    time_slot: TimeSlotCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Create new time slot"""
    return time_slot_service.create_time_slot(db, time_slot)

@router.get("/coffee-shops/{coffee_shop_id}/time-slots", response_model=List[TimeSlot])
async def get_coffee_shop_time_slots(
    coffee_shop_id: UUID,
    active_only: bool = False,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get all time slots for a coffee shop"""
    return time_slot_service.get_all_for_coffee_shop(db, coffee_shop_id, active_only)

@router.put("/time-slots/{time_slot_id}", response_model=TimeSlot)
async def update_time_slot(
    time_slot_id: UUID,
    time_slot_data: TimeSlotUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Update time slot"""
    time_slot = time_slot_service.update_time_slot(
        db, time_slot_id, time_slot_data
    )
    if not time_slot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time slot not found"
        )
    return time_slot

@router.delete("/time-slots/{time_slot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_time_slot(
    time_slot_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Delete time slot"""
    success = time_slot_service.delete_time_slot(db, time_slot_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time slot not found"
        )
    return {"detail": "Time slot deleted successfully"}

@router.put("/coffee-shops/{coffee_shop_id}/time-slots", response_model=List[TimeSlot])
async def batch_update_time_slots(
    coffee_shop_id: UUID,
    time_slots_data: BatchTimeSlotUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Batch update time slots for a coffee shop"""
    return time_slot_service.batch_update_time_slots(
        db, coffee_shop_id, time_slots_data.time_slots
    )