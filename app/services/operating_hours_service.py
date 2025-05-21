"""
Service for operating hours and time slots
"""
from datetime import time
from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.operating_hours import WeekDay
from app.repositories.operating_hours_repository import operating_hours_repository, time_slot_repository
from app.schemas.operating_hours_schema import (
    OperatingHoursCreate, 
    OperatingHoursUpdate, 
    TimeSlotCreate, 
    TimeSlotUpdate
)

class OperatingHoursService:
    def create_operating_hours(
        self, db: Session, operating_hours_data: OperatingHoursCreate
    ):
        """Create new operating hours"""
        # Check if operating hours already exist for this day
        existing = operating_hours_repository.get_by_day_for_coffee_shop(
            db, 
            operating_hours_data.coffee_shop_id,
            operating_hours_data.day
        )
        
        if existing:
            # If exists, update instead
            for key, value in operating_hours_data.dict().items():
                setattr(existing, key, value)
            db.commit()
            db.refresh(existing)
            return existing
        
        # Otherwise create new
        return operating_hours_repository.create_operating_hours(
            db, operating_hours_data=operating_hours_data
        )
    
    def update_operating_hours(
        self, 
        db: Session, 
        operating_hours_id: UUID, 
        operating_hours_data: OperatingHoursUpdate
    ):
        """Update operating hours"""
        return operating_hours_repository.update_operating_hours(
            db, 
            operating_hours_id=operating_hours_id, 
            operating_hours_data=operating_hours_data
        )
    
    def get_operating_hours(self, db: Session, operating_hours_id: UUID):
        """Get operating hours by id"""
        return operating_hours_repository.get_operating_hours(db, operating_hours_id)
    
    def get_all_for_coffee_shop(self, db: Session, coffee_shop_id: UUID):
        """Get all operating hours for a coffee shop"""
        return operating_hours_repository.get_all_for_coffee_shop(db, coffee_shop_id)
    
    def batch_update_operating_hours(
        self, db: Session, coffee_shop_id: UUID, operating_hours_list: List[OperatingHoursCreate]
    ):
        """Update or create all operating hours for a coffee shop"""
        result = []
        for oh_data in operating_hours_list:
            # Ensure coffee shop id is consistent
            oh_data.coffee_shop_id = coffee_shop_id
            
            # Create or update
            oh = self.create_operating_hours(db, oh_data)
            result.append(oh)
        
        return result
    
    def delete_operating_hours(self, db: Session, operating_hours_id: UUID) -> bool:
        """Delete operating hours"""
        return operating_hours_repository.delete_operating_hours(db, operating_hours_id)

class TimeSlotService:
    def create_time_slot(self, db: Session, time_slot_data: TimeSlotCreate):
        """Create new time slot"""
        return time_slot_repository.create_time_slot(
            db, time_slot_data=time_slot_data
        )
    
    def update_time_slot(
        self, 
        db: Session, 
        time_slot_id: UUID, 
        time_slot_data: TimeSlotUpdate
    ):
        """Update time slot"""
        return time_slot_repository.update_time_slot(
            db, 
            time_slot_id=time_slot_id, 
            time_slot_data=time_slot_data
        )
    
    def get_time_slot(self, db: Session, time_slot_id: UUID):
        """Get time slot by id"""
        return time_slot_repository.get_time_slot(db, time_slot_id)
    
    def get_all_for_coffee_shop(
        self, db: Session, coffee_shop_id: UUID, active_only: bool = False
    ):
        """Get all time slots for a coffee shop"""
        return time_slot_repository.get_all_for_coffee_shop(
            db, coffee_shop_id, active_only
        )
    
    def batch_update_time_slots(
        self, db: Session, coffee_shop_id: UUID, time_slots_list: List[TimeSlotCreate]
    ):
        """Update or create time slots in batch"""
        # First, delete all existing time slots
        existing = self.get_all_for_coffee_shop(db, coffee_shop_id)
        for slot in existing:
            time_slot_repository.delete_time_slot(db, slot.id)
        
        # Then create new ones
        result = []
        for slot_data in time_slots_list:
            # Ensure coffee shop id is consistent
            slot_data.coffee_shop_id = coffee_shop_id
            
            # Create new
            slot = self.create_time_slot(db, slot_data)
            result.append(slot)
        
        return result
    
    def delete_time_slot(self, db: Session, time_slot_id: UUID) -> bool:
        """Delete time slot"""
        return time_slot_repository.delete_time_slot(db, time_slot_id)

operating_hours_service = OperatingHoursService()
time_slot_service = TimeSlotService()