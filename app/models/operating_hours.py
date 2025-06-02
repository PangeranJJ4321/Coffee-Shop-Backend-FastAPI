import enum
from datetime import time
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Enum, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.models.base import BaseModel

class WeekDay(enum.Enum):
    """Days of the week enum"""
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"

class TimeSlotModel(BaseModel):
    """Time slot model for booking sessions"""
    __tablename__ = "time_slots"
    
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    max_capacity = Column(Integer, nullable=False, default=0)  # Maximum guests allowed per slot
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Foreign keys
    coffee_shop_id = Column(UUID(as_uuid=True), ForeignKey("coffee_shops.id"), nullable=False)
    
    # Relationships
    coffee_shop = relationship("CoffeeShopModel", back_populates="time_slots")
    
    def __repr__(self):
        return f"<TimeSlot {self.start_time}-{self.end_time}>"

class OperatingHoursModel(BaseModel):
    """Operating hours model for coffee shop"""
    __tablename__ = "operating_hours"
    
    day = Column(Enum(WeekDay), nullable=False)
    opening_time = Column(Time, nullable=False)
    closing_time = Column(Time, nullable=False)
    is_open = Column(Boolean, default=True, nullable=False)
    
    # Foreign keys
    coffee_shop_id = Column(UUID(as_uuid=True), ForeignKey("coffee_shops.id"), nullable=False)
    
    # Relationships
    coffee_shop = relationship("CoffeeShopModel", back_populates="operating_hours")
    
    def __repr__(self):
        return f"<OperatingHours {self.day.value} {self.opening_time}-{self.closing_time}>"