"""
Schemas for table bookings
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date, time
from pydantic import BaseModel, Field, validator

from app.models.booking import BookingStatus


class TableResponse(BaseModel):
    id: UUID
    table_number: str
    capacity: int

    class Config:
        from_attributes = True


class BookingTableCreate(BaseModel):
    table_id: UUID


class BookingCreate(BaseModel):
    coffee_shop_id: UUID
    booking_date: datetime
    guest_count: int = Field(..., gt=0)
    table_ids: Optional[List[UUID]] = None  # If null, system will auto-assign tables

    @validator('guest_count')
    def guest_count_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Guest count must be positive')
        return v


class BookingUpdate(BaseModel):
    booking_date: Optional[datetime] = None
    guest_count: Optional[int] = None
    
    @validator('guest_count')
    def guest_count_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Guest count must be positive')
        return v


class BookingResponse(BaseModel):
    id: UUID
    booking_id: str
    table_count: int
    guest_count: int
    status: BookingStatus
    booking_date: datetime

    class Config:
        from_attributes = True


class BookingTableResponse(BaseModel):
    id: UUID
    table: TableResponse

    class Config:
        from_attributes = True


class BookingWithTablesResponse(BookingResponse):
    booking_tables: List[BookingTableResponse]

    class Config:
        from_attributes = True


class AvailableTable(BaseModel):
    id: UUID
    table_number: str
    capacity: int


class AvailableSlot(BaseModel):
    start_time: time
    end_time: time
    available_tables: List[AvailableTable]
    total_capacity: int