"""
Routes for table booking management
"""
from typing import List
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import UserModel
from app.schemas.booking_schema import (
    BookingCreate,
    BookingResponse,
    BookingUpdate,
    AvailableSlot,
    BookingWithTablesResponse
)
from app.services.booking_service import booking_service
from app.utils.security import get_current_user

router = APIRouter(prefix="/bookings", tags=["Table Bookings"])

@router.get("/availability", response_model=List[AvailableSlot])
async def check_availability(
    coffee_shop_id: UUID,
    booking_date: date,
    guests: int = Query(..., gt=0),
    db: Session = Depends(get_db)
):
    """Check available time slots and tables for a specific date and guest count"""
    return booking_service.get_available_slots(db, coffee_shop_id, booking_date, guests)

@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Create a new table booking"""
    booking = booking_service.create_booking(db, booking_data, current_user.id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to create booking. Tables might not be available for the requested time and guest count."
        )
    return booking

@router.get("/", response_model=List[BookingResponse])
async def get_user_bookings(
    status: str = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get all bookings for the current user with optional status filtering"""
    return booking_service.get_user_bookings(db, current_user.id, status)

@router.get("/{booking_id}", response_model=BookingWithTablesResponse)
async def get_booking_details(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get detailed information about a specific booking"""
    booking = booking_service.get_booking_by_id(db, booking_id, current_user.id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    return booking

@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: UUID,
    booking_data: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Update an existing booking (only allowed for unconfirmed bookings)"""
    booking = booking_service.update_booking(db, booking_id, booking_data, current_user.id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to update booking. Booking might be already confirmed or not found."
        )
    return booking

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Cancel a booking"""
    success = booking_service.cancel_booking(db, booking_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to cancel booking. Booking might be already confirmed or not found."
        )
    return {"detail": "Booking cancelled successfully"}