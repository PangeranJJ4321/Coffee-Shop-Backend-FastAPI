"""
Repository for operating hours and time slots
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.models.operating_hours import OperatingHoursModel, TimeSlotModel, WeekDay

class OperatingHoursRepository:
    def create_operating_hours(self, db: Session, *, operating_hours_data) -> OperatingHoursModel:
        """Create new operating hours"""
        operating_hours = OperatingHoursModel(**operating_hours_data.dict())
        db.add(operating_hours)
        db.commit()
        db.refresh(operating_hours)
        return operating_hours
    
    def update_operating_hours(
        self, db: Session, *, operating_hours_id: UUID, operating_hours_data
    ) -> Optional[OperatingHoursModel]:
        """Update operating hours"""
        operating_hours = db.query(OperatingHoursModel).filter(
            OperatingHoursModel.id == operating_hours_id
        ).first()
        if not operating_hours:
            return None
        
        for key, value in operating_hours_data.dict(exclude_unset=True).items():
            setattr(operating_hours, key, value)
        
        db.commit()
        db.refresh(operating_hours)
        return operating_hours
    
    def get_operating_hours(self, db: Session, operating_hours_id: UUID) -> Optional[OperatingHoursModel]:
        """Get operating hours by id"""
        return db.query(OperatingHoursModel).filter(
            OperatingHoursModel.id == operating_hours_id
        ).first()
    
    def get_all_for_coffee_shop(
        self, db: Session, coffee_shop_id: UUID
    ) -> List[OperatingHoursModel]:
        """Get all operating hours for a coffee shop"""
        return db.query(OperatingHoursModel).filter(
            OperatingHoursModel.coffee_shop_id == coffee_shop_id
        ).all()
    
    def get_by_day_for_coffee_shop(
        self, db: Session, coffee_shop_id: UUID, day: WeekDay
    ) -> Optional[OperatingHoursModel]:
        """Get operating hours for a specific day"""
        return db.query(OperatingHoursModel).filter(
            OperatingHoursModel.coffee_shop_id == coffee_shop_id,
            OperatingHoursModel.day == day
        ).first()
    
    def delete_operating_hours(self, db: Session, operating_hours_id: UUID) -> bool:
        """Delete operating hours"""
        operating_hours = db.query(OperatingHoursModel).filter(
            OperatingHoursModel.id == operating_hours_id
        ).first()
        if not operating_hours:
            return False
        
        db.delete(operating_hours)
        db.commit()
        return True

class TimeSlotRepository:
    def create_time_slot(self, db: Session, *, time_slot_data) -> TimeSlotModel:
        """Create new time slot"""
        time_slot = TimeSlotModel(**time_slot_data.dict())
        db.add(time_slot)
        db.commit()
        db.refresh(time_slot)
        return time_slot
    
    def update_time_slot(
        self, db: Session, *, time_slot_id: UUID, time_slot_data
    ) -> Optional[TimeSlotModel]:
        """Update time slot"""
        time_slot = db.query(TimeSlotModel).filter(
            TimeSlotModel.id == time_slot_id
        ).first()
        if not time_slot:
            return None
        
        for key, value in time_slot_data.dict(exclude_unset=True).items():
            setattr(time_slot, key, value)
        
        db.commit()
        db.refresh(time_slot)
        return time_slot
    
    def get_time_slot(self, db: Session, time_slot_id: UUID) -> Optional[TimeSlotModel]:
        """Get time slot by id"""
        return db.query(TimeSlotModel).filter(
            TimeSlotModel.id == time_slot_id
        ).first()
    
    def get_all_for_coffee_shop(
        self, db: Session, coffee_shop_id: UUID, active_only: bool = False
    ) -> List[TimeSlotModel]:
        """Get all time slots for a coffee shop"""
        query = db.query(TimeSlotModel).filter(
            TimeSlotModel.coffee_shop_id == coffee_shop_id
        )
        
        if active_only:
            query = query.filter(TimeSlotModel.is_active == True)
            
        return query.all()
    
    def delete_time_slot(self, db: Session, time_slot_id: UUID) -> bool:
        """Delete time slot"""
        time_slot = db.query(TimeSlotModel).filter(
            TimeSlotModel.id == time_slot_id
        ).first()
        if not time_slot:
            return False
        
        db.delete(time_slot)
        db.commit()
        return True

operating_hours_repository = OperatingHoursRepository()
time_slot_repository = TimeSlotRepository()