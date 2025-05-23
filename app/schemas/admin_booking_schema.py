"""
Schemas for admin booking management
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.booking import BookingStatus

class BookingStatusUpdate(BaseModel):
    status: BookingStatus
    notes: Optional[str] = Field(None, description="Optional notes for status change")

class BulkBookingStatusUpdate(BaseModel):
    booking_ids: List[UUID] = Field(..., description="List of booking IDs to update")
    status: BookingStatus
    notes: Optional[str] = Field(None, description="Optional notes for status change")

class BookingManagementResponse(BaseModel):
    id: UUID
    booking_id: str
    status: BookingStatus
    booking_date: datetime
    guest_count: int
    table_count: int
    user_id: UUID
    user_name: str
    user_email: str
    coffee_shop_id: UUID
    coffee_shop_name: str
    table_numbers: List[str]  # List of table numbers assigned
    special_requests: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BookingStatusHistoryResponse(BaseModel):
    id: UUID
    booking_id: UUID
    old_status: Optional[BookingStatus] = None
    new_status: BookingStatus
    changed_by_user_id: UUID
    changed_by_user_name: str
    notes: Optional[str] = None
    changed_at: datetime

    class Config:
        from_attributes = True

class TodayBookingsSummary(BaseModel):
    total_bookings: int
    confirmed_bookings: int
    pending_bookings: int
    cancelled_bookings: int
    completed_bookings: int
    total_guests: int
    peak_time_slot: Optional[str] = None
    occupancy_rate: float  # Percentage