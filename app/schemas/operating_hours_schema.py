"""
Operating hours and time slot schemas
"""
from datetime import time
from enum import Enum
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class WeekDay(str, Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"

# Time Slot Schemas
class TimeSlotBase(BaseModel):
    start_time: time
    end_time: time
    max_capacity: int = Field(..., ge=0)
    is_active: bool = True

class TimeSlotCreate(TimeSlotBase):
    coffee_shop_id: UUID

class TimeSlotUpdate(BaseModel):
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    max_capacity: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

class TimeSlotInDBBase(TimeSlotBase):
    id: UUID
    coffee_shop_id: UUID
    
    class Config:
        orm_mode = True

class TimeSlot(TimeSlotInDBBase):
    pass

# Operating Hours Schemas
class OperatingHoursBase(BaseModel):
    day: WeekDay
    opening_time: time
    closing_time: time
    is_open: bool = True

class OperatingHoursCreate(OperatingHoursBase):
    coffee_shop_id: UUID

class OperatingHoursUpdate(BaseModel):
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None
    is_open: Optional[bool] = None

class OperatingHoursInDBBase(OperatingHoursBase):
    id: UUID
    coffee_shop_id: UUID
    
    class Config:
        orm_mode = True

class OperatingHours(OperatingHoursInDBBase):
    pass

# Batch update schemas
class BatchOperatingHoursUpdate(BaseModel):
    operating_hours: List[OperatingHoursCreate]

class BatchTimeSlotUpdate(BaseModel):
    time_slots: List[TimeSlotCreate]