"""
Controller for admin booking status management
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import UserModel
from app.schemas.admin_booking_schema import (
    BookingStatusUpdate,
    BookingManagementResponse,
    BookingStatusHistoryResponse,
    BulkBookingStatusUpdate
)
from app.services.notification_services import notification_service
from app.services.admin_booking_services import admin_booking_service as services
from app.utils.security import get_current_admin_user
from app.models.booking import BookingStatus

router = APIRouter(prefix="/booking-status", tags=["Admin ~ Booking Status Management"])

@router.get("/bookings", response_model=List[BookingManagementResponse])
async def get_all_bookings(
    status: Optional[BookingStatus] = Query(None, description="Filter by booking status"),
    coffee_shop_id: Optional[UUID] = Query(None, description="Filter by coffee shop"),
    user_id: Optional[UUID] = Query(None, description="Filter by user"),
    booking_date: Optional[str] = Query(None, description="Filter by booking date (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get all bookings with filtering options (Admin only)"""
    return services.get_all_bookings(
        db, status=status, coffee_shop_id=coffee_shop_id,
        user_id=user_id, booking_date=booking_date,
        skip=skip, limit=limit
    )

@router.get("/bookings/{booking_id}", response_model=BookingManagementResponse)
async def get_booking_details(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get detailed booking information (Admin only)"""
    booking = services.get_booking_by_id(db, booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    return booking

@router.put("/bookings/{booking_id}/status", response_model=BookingManagementResponse)
async def update_booking_status(
    booking_id: UUID,
    status_update: BookingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Update booking status and send notification (Admin only)"""
    # Update booking status
    updated_booking = services.update_booking_status(
        db, booking_id, status_update.status, status_update.notes
    )
    
    if not updated_booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Send notification to user
    try:
        await notification_service.send_booking_status_notification(
            db, booking_id, status_update.status, current_user.id
        )
    except Exception as e:
        # Log error but don't fail the request
        print(f"Failed to send notification: {str(e)}")
    
    return updated_booking

@router.get("/bookings/{booking_id}/status-history", response_model=List[BookingStatusHistoryResponse])
async def get_booking_status_history(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get booking status change history (Admin only)"""
    history = services.get_booking_status_history(db, booking_id)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found or no status history available"
        )
    return history

@router.put("/bookings/bulk-status-update", response_model=List[BookingManagementResponse])
async def bulk_update_booking_status(
    bulk_update: BulkBookingStatusUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Bulk update booking statuses (Admin only)"""
    updated_bookings = services.bulk_update_booking_status(
        db, bulk_update.booking_ids, bulk_update.status, bulk_update.notes
    )
    
    # Send notifications for each updated booking
    for booking in updated_bookings:
        try:
            await notification_service.send_booking_status_notification(
                db, booking.id, bulk_update.status, current_user.id
            )
        except Exception as e:
            print(f"Failed to send notification for booking {booking.id}: {str(e)}")
    
    return updated_bookings

@router.get("/bookings/today/summary")
async def get_today_bookings_summary(
    coffee_shop_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get today's bookings summary (Admin only)"""
    summary = services.get_today_bookings_summary(db, coffee_shop_id)
    return summary

@router.get("/bookings/upcoming/count")
async def get_upcoming_bookings_count(
    coffee_shop_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get count of upcoming bookings (Admin only)"""
    count = services.get_upcoming_bookings_count(db, coffee_shop_id)
    return {"upcoming_bookings_count": count}