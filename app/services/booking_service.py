"""
Service for handling table booking operations
"""
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import date, datetime, time, timedelta
import uuid
import random
import string
from sqlalchemy import and_, or_, func, cast, Date
from sqlalchemy.orm import Session, joinedload

from app.models.booking import BookingModel, BookingTableModel, BookingStatus, TableModel
from app.models.coffee import CoffeeShopModel
from app.models.operating_hours import TimeSlotModel, OperatingHoursModel, WeekDay
from app.schemas.booking_schema import (
    BookingCreate, 
    BookingUpdate, 
    AvailableSlot, 
    AvailableTable
)


class BookingService:
    def generate_booking_id(self) -> str:
        """Generate a unique booking ID"""
        # Format: BK-YYYYMMDD-XXXXX where XXXXX is random alphanumeric
        today = datetime.now().strftime("%Y%m%d")
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        return f"BK-{today}-{random_suffix}"
    
    def get_available_slots(
        self, 
        db: Session, 
        coffee_shop_id: UUID, 
        booking_date: date, 
        guests: int
    ) -> List[AvailableSlot]:
        """
        Get available time slots and tables for a specific date and guest count
        """
        # Get day of week for the booking date
        weekday = WeekDay[booking_date.strftime("%A").upper()]
        
        # Get operating hours for that day
        operating_hours = db.query(OperatingHoursModel).filter(
            OperatingHoursModel.coffee_shop_id == coffee_shop_id,
            OperatingHoursModel.day == weekday,
            OperatingHoursModel.is_open == True
        ).first()
        
        if not operating_hours:
            return []  # Coffee shop is closed on this day
        
        # Get time slots for the coffee shop
        time_slots = db.query(TimeSlotModel).filter(
            TimeSlotModel.coffee_shop_id == coffee_shop_id,
            TimeSlotModel.is_active == True,
            TimeSlotModel.start_time >= operating_hours.opening_time,
            TimeSlotModel.end_time <= operating_hours.closing_time
        ).order_by(TimeSlotModel.start_time).all()
        
        if not time_slots:
            return []  # No time slots configured
        
        # Get all tables for the coffee shop
        tables = db.query(TableModel).filter(
            TableModel.coffee_shop_id == coffee_shop_id,
            TableModel.is_available == True
        ).order_by(TableModel.capacity).all()
        
        if not tables:
            return []  # No tables available
        
        # Get all bookings for that date
        booking_date_start = datetime.combine(booking_date, time.min)
        booking_date_end = datetime.combine(booking_date, time.max)
        
        existing_bookings = db.query(BookingModel).filter(
            BookingModel.booking_date >= booking_date_start,
            BookingModel.booking_date <= booking_date_end,
            BookingModel.status.in_([BookingStatus.NOCONFIRM, BookingStatus.CONFIRM, BookingStatus.SUCCESS])
        ).all()
        
        # Get all booked tables for each time slot
        booked_tables_by_slot = {}
        for booking in existing_bookings:
            # Extract time part
            booking_time = booking.booking_date.time()
            
            # Find which time slot this booking belongs to
            for slot in time_slots:
                if slot.start_time <= booking_time < slot.end_time:
                    if slot.id not in booked_tables_by_slot:
                        booked_tables_by_slot[slot.id] = set()
                    
                    # Get tables associated with this booking
                    booking_tables = db.query(BookingTableModel).filter(
                        BookingTableModel.booking_id == booking.id
                    ).all()
                    
                    for bt in booking_tables:
                        booked_tables_by_slot[slot.id].add(bt.table_id)
        
        # Prepare response with available tables for each slot
        result = []
        for slot in time_slots:
            booked_tables = booked_tables_by_slot.get(slot.id, set())
            available_tables = []
            total_capacity = 0
            
            # Determine which tables are available
            for table in tables:
                if table.id not in booked_tables:
                    available_tables.append(
                        AvailableTable(
                            id=table.id,
                            table_number=table.table_number,
                            capacity=table.capacity
                        )
                    )
                    total_capacity += table.capacity
            
            # Check if the slot has enough capacity for the guest count
            if total_capacity >= guests:
                result.append(
                    AvailableSlot(
                        start_time=slot.start_time,
                        end_time=slot.end_time,
                        available_tables=available_tables,
                        total_capacity=total_capacity
                    )
                )
        
        return result
    
    def find_suitable_tables(
        self, 
        db: Session, 
        coffee_shop_id: UUID, 
        booking_date: datetime, 
        guest_count: int
    ) -> List[TableModel]:
        """
        Algorithm to find suitable tables for the given guest count
        Returns list of tables that can accommodate the guests
        Uses a greedy approach to minimize the number of tables used
        """
        # Get all tables from the coffee shop
        all_tables = db.query(TableModel).filter(
            TableModel.coffee_shop_id == coffee_shop_id,
            TableModel.is_available == True
        ).order_by(TableModel.capacity.desc()).all()
        
        # Get bookings for the same time slot to find already booked tables
        booking_time = booking_date.time()
        booking_date_start = datetime.combine(booking_date.date(), time.min)
        booking_date_end = datetime.combine(booking_date.date(), time.max)
        
        # Find time slot for the booking time
        time_slot = db.query(TimeSlotModel).filter(
            TimeSlotModel.coffee_shop_id == coffee_shop_id,
            TimeSlotModel.start_time <= booking_time,
            TimeSlotModel.end_time > booking_time,
            TimeSlotModel.is_active == True
        ).first()
        
        if not time_slot:
            return []  # No valid time slot
        
        # Get existing bookings for this time slot
        existing_bookings = db.query(BookingModel).filter(
            BookingModel.booking_date >= booking_date_start,
            BookingModel.booking_date <= booking_date_end,
            BookingModel.status.in_([BookingStatus.NOCONFIRM, BookingStatus.CONFIRM, BookingStatus.SUCCESS])
        ).all()
        
        # Find already booked tables
        booked_table_ids = set()
        for booking in existing_bookings:
            booking_time = booking.booking_date.time()
            
            # Check if this booking overlaps with the requested time slot
            if time_slot.start_time <= booking_time < time_slot.end_time:
                booking_tables = db.query(BookingTableModel).filter(
                    BookingTableModel.booking_id == booking.id
                ).all()
                
                for bt in booking_tables:
                    booked_table_ids.add(bt.table_id)
        
        # Filter out already booked tables
        available_tables = [table for table in all_tables if table.id not in booked_table_ids]
        
        # If no tables available, return empty list
        if not available_tables:
            return []
        
        # Use greedy algorithm to find tables
        selected_tables = []
        remaining_guests = guest_count
        
        # First try to find a single table that fits all guests
        for table in available_tables:
            if table.capacity >= guest_count:
                return [table]  # Found a single table that fits all guests
        
        # If no single table fits all, use multiple tables
        for table in available_tables:
            if remaining_guests <= 0:
                break
            
            selected_tables.append(table)
            remaining_guests -= table.capacity
        
        # Check if we found enough tables
        if remaining_guests <= 0:
            return selected_tables
        else:
            return []  # Not enough capacity
    
    def create_booking(
        self, 
        db: Session, 
        booking_data: BookingCreate, 
        user_id: UUID
    ) -> Optional[BookingModel]:
        """
        Create a new booking with associated tables
        If table_ids not provided, system will auto-assign tables
        """
        tables_to_book = []
        
        if booking_data.table_ids:
            # Use user-selected tables
            tables_to_book = db.query(TableModel).filter(
                TableModel.id.in_(booking_data.table_ids),
                TableModel.coffee_shop_id == booking_data.coffee_shop_id,
                TableModel.is_available == True
            ).all()
            
            # Verify all requested tables exist and belong to the coffee shop
            if len(tables_to_book) != len(booking_data.table_ids):
                return None
            
            # Check if tables are already booked
            if not self._check_tables_availability(db, tables_to_book, booking_data.booking_date):
                return None
                
            # Calculate total capacity to ensure it's enough
            total_capacity = sum(table.capacity for table in tables_to_book)
            if total_capacity < booking_data.guest_count:
                return None  # Not enough capacity
        else:
            # Auto-assign tables
            tables_to_book = self.find_suitable_tables(
                db, 
                booking_data.coffee_shop_id, 
                booking_data.booking_date, 
                booking_data.guest_count
            )
            
            if not tables_to_book:
                return None  # Couldn't find suitable tables
        
        # Create the booking
        booking = BookingModel(
            booking_id=self.generate_booking_id(),
            table_count=len(tables_to_book),
            guest_count=booking_data.guest_count,
            status=BookingStatus.NOCONFIRM,
            booking_date=booking_data.booking_date,
            user_id=user_id
        )
        
        db.add(booking)
        db.flush()  # To get the booking ID
        
        # Create booking table associations
        for table in tables_to_book:
            booking_table = BookingTableModel(
                booking_id=booking.id,
                table_id=table.id
            )
            db.add(booking_table)
        
        db.commit()
        db.refresh(booking)
        return booking
    
    def _check_tables_availability(
        self, 
        db: Session, 
        tables: List[TableModel], 
        booking_date: datetime
    ) -> bool:
        """Check if tables are available for the requested time"""
        table_ids = [table.id for table in tables]
        booking_time = booking_date.time()
        booking_date_start = datetime.combine(booking_date.date(), time.min)
        booking_date_end = datetime.combine(booking_date.date(), time.max)
        
        # Find time slot for the booking time
        time_slot = db.query(TimeSlotModel).filter(
            TimeSlotModel.coffee_shop_id == tables[0].coffee_shop_id,
            TimeSlotModel.start_time <= booking_time,
            TimeSlotModel.end_time > booking_time,
            TimeSlotModel.is_active == True
        ).first()
        
        if not time_slot:
            return False  # No valid time slot
        
        # Get existing bookings for the same date
        existing_bookings = db.query(BookingModel).filter(
            BookingModel.booking_date >= booking_date_start,
            BookingModel.booking_date <= booking_date_end,
            BookingModel.status.in_([BookingStatus.NOCONFIRM, BookingStatus.CONFIRM, BookingStatus.SUCCESS])
        ).all()
        
        # Check for conflicts
        for booking in existing_bookings:
            booking_time = booking.booking_date.time()
            
            # Check if this booking overlaps with the requested time slot
            if time_slot.start_time <= booking_time < time_slot.end_time:
                # Get tables for this booking
                booking_tables = db.query(BookingTableModel).filter(
                    BookingTableModel.booking_id == booking.id
                ).all()
                
                booked_table_ids = {bt.table_id for bt in booking_tables}
                
                # Check for intersection
                if any(table_id in booked_table_ids for table_id in table_ids):
                    return False  # Conflict found
        
        return True  # No conflicts
    
    def get_user_bookings(
        self, 
        db: Session, 
        user_id: UUID, 
        status: Optional[str] = None
    ) -> List[BookingModel]:
        """Get all bookings for a user with optional status filtering"""
        query = db.query(BookingModel).filter(BookingModel.user_id == user_id)
        
        if status:
            try:
                booking_status = BookingStatus[status.upper()]
                query = query.filter(BookingModel.status == booking_status)
            except KeyError:
                # Invalid status, ignore filter
                pass
        
        return query.order_by(BookingModel.booking_date.desc()).all()
    
    def get_booking_by_id(
        self, 
        db: Session, 
        booking_id: UUID, 
        user_id: UUID
    ) -> Optional[BookingModel]:
        """Get booking details by ID for a specific user"""
        return db.query(BookingModel).options(
            joinedload(BookingModel.booking_tables).joinedload(BookingTableModel.table)
        ).filter(
            BookingModel.id == booking_id,
            BookingModel.user_id == user_id
        ).first()
    
    def update_booking(
        self, 
        db: Session, 
        booking_id: UUID, 
        booking_data: BookingUpdate, 
        user_id: UUID
    ) -> Optional[BookingModel]:
        """Update an existing booking (only for unconfirmed bookings)"""
        booking = db.query(BookingModel).filter(
            BookingModel.id == booking_id,
            BookingModel.user_id == user_id,
            BookingModel.status == BookingStatus.NOCONFIRM
        ).first()
        
        if not booking:
            return None  # Booking not found or not updatable
        
        # Handle date/time update
        if booking_data.booking_date:
            # Check if tables are still available for new date/time
            booking_tables = db.query(BookingTableModel).filter(
                BookingTableModel.booking_id == booking.id
            ).all()
            
            tables = [bt.table for bt in booking_tables]
            
            if not self._check_tables_availability(db, tables, booking_data.booking_date):
                return None  # Tables not available for new date/time
            
            booking.booking_date = booking_data.booking_date
        
        # Handle guest count update
        if booking_data.guest_count:
            # Check if current tables can accommodate new guest count
            booking_tables = db.query(BookingTableModel).filter(
                BookingTableModel.booking_id == booking.id
            ).all()
            
            total_capacity = sum(bt.table.capacity for bt in booking_tables)
            
            if total_capacity < booking_data.guest_count:
                return None  # Not enough capacity
            
            booking.guest_count = booking_data.guest_count
        
        db.commit()
        db.refresh(booking)
        return booking
    
    def cancel_booking(
        self, 
        db: Session, 
        booking_id: UUID, 
        user_id: UUID
    ) -> bool:
        """Cancel a booking"""
        booking = db.query(BookingModel).filter(
            BookingModel.id == booking_id,
            BookingModel.user_id == user_id,
            BookingModel.status.in_([BookingStatus.NOCONFIRM, BookingStatus.CONFIRM])
        ).first()
        
        if not booking:
            return False  # Booking not found or not cancellable
        
        booking.status = BookingStatus.CANCELLED
        db.commit()
        return True

    def get_upcoming_bookings(
        self, 
        db: Session, 
        hours_ahead: int = 24
    ) -> List[BookingModel]:
        """Get bookings coming up in the next X hours for reminders"""
        now = datetime.now()
        reminder_window = now + timedelta(hours=hours_ahead)
        
        return db.query(BookingModel).filter(
            BookingModel.booking_date >= now,
            BookingModel.booking_date <= reminder_window,
            BookingModel.status.in_([BookingStatus.CONFIRM, BookingStatus.SUCCESS]),
            BookingModel.booking_reminder_sent == False
        ).all()
    
    def mark_reminder_sent(
        self, 
        db: Session, 
        booking_id: UUID
    ) -> bool:
        """Mark a booking as having had its reminder sent"""
        booking = db.query(BookingModel).filter(BookingModel.id == booking_id).first()
        
        if not booking:
            return False
        
        booking.booking_reminder_sent = True
        db.commit()
        return True


# Create singleton instance
booking_service = BookingService()