"""
Service for admin booking management
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc

from app.models.booking import BookingModel, BookingStatus, BookingTableModel
from app.models.user import UserModel
from app.models.coffee_shop import CoffeeShopModel
from app.models.table import TableModel
from app.schemas.admin_booking_schema import (
    BookingManagementResponse,
    BookingStatusHistoryResponse,
    TodayBookingsSummary
)

class AdminBookingService:
    def get_all_bookings(
        self, 
        db: Session, 
        status: Optional[BookingStatus] = None,
        coffee_shop_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        booking_date: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[BookingManagementResponse]:
        """Get all bookings with filtering"""
        query = db.query(BookingModel).options(
            joinedload(BookingModel.user),
            joinedload(BookingModel.coffee_shop),
            joinedload(BookingModel.booking_tables).joinedload(BookingTableModel.table)
        )
        
        # Apply filters
        if status:
            query = query.filter(BookingModel.status == status)
        if coffee_shop_id:
            query = query.filter(BookingModel.coffee_shop_id == coffee_shop_id)
        if user_id:
            query = query.filter(BookingModel.user_id == user_id)
        if booking_date:
            try:
                target_date = datetime.strptime(booking_date, "%Y-%m-%d").date()
                query = query.filter(func.date(BookingModel.booking_date) == target_date)
            except ValueError:
                pass  # Invalid date format, ignore filter
        
        bookings = query.order_by(desc(BookingModel.created_at)).offset(skip).limit(limit).all()
        
        # Convert to response format
        result = []
        for booking in bookings:
            # Get table numbers
            table_numbers = [bt.table.table_number for bt in booking.booking_tables]
            
            result.append(BookingManagementResponse(
                id=booking.id,
                booking_id=booking.booking_id,
                status=booking.status,
                booking_date=booking.booking_date,
                guest_count=booking.guest_count,
                table_count=booking.table_count,
                user_id=booking.user_id,
                user_name=booking.user.full_name,
                user_email=booking.user.email,
                coffee_shop_id=booking.coffee_shop_id,
                coffee_shop_name=booking.coffee_shop.name,
                table_numbers=table_numbers,
                special_requests=getattr(booking, 'special_requests', None),
                created_at=booking.created_at,
                updated_at=booking.updated_at
            ))
        
        return result
    
    def get_booking_by_id(self, db: Session, booking_id: UUID):
        """Get booking by ID with all details"""
        booking = db.query(BookingModel).options(
            joinedload(BookingModel.user),
            joinedload(BookingModel.coffee_shop),
            joinedload(BookingModel.booking_tables).joinedload(BookingTableModel.table)
        ).filter(BookingModel.id == booking_id).first()
        
        if not booking:
            return None
        
        # Convert to response format
        table_numbers = [bt.table.table_number for bt in booking.booking_tables]
        
        return BookingManagementResponse(
            id=booking.id,
            booking_id=booking.booking_id,
            status=booking.status,
            booking_date=booking.booking_date,
            guest_count=booking.guest_count,
            table_count=booking.table_count,
            user_id=booking.user_id,
            user_name=booking.user.full_name,
            user_email=booking.user.email,
            coffee_shop_id=booking.coffee_shop_id,
            coffee_shop_name=booking.coffee_shop.name,
            table_numbers=table_numbers,
            special_requests=getattr(booking, 'special_requests', None),
            created_at=booking.created_at,
            updated_at=booking.updated_at
        )
    
    def update_booking_status(
        self, 
        db: Session, 
        booking_id: UUID, 
        new_status: BookingStatus,
        notes: Optional[str] = None
    ):
        """Update booking status and create history record"""
        booking = db.query(BookingModel).filter(BookingModel.id == booking_id).first()
        if not booking:
            return None
        
        old_status = booking.status
        booking.status = new_status
        booking.updated_at = datetime.utcnow()
        
        # Create status history record (you'll need to create this model)
        # status_history = BookingStatusHistoryModel(
        #     booking_id=booking_id,
        #     old_status=old_status,
        #     new_status=new_status,
        #     changed_by_user_id=changed_by_user_id,
        #     notes=notes,
        #     changed_at=datetime.utcnow()
        # )
        # db.add(status_history)
        
        db.commit()
        db.refresh(booking)
        
        return self.get_booking_by_id(db, booking_id)
    
    def bulk_update_booking_status(
        self,
        db: Session,
        booking_ids: List[UUID],
        new_status: BookingStatus,
        notes: Optional[str] = None
    ):
        """Bulk update booking statuses"""
        bookings = db.query(BookingModel).filter(BookingModel.id.in_(booking_ids)).all()
        updated_bookings = []
        
        for booking in bookings:
            old_status = booking.status
            booking.status = new_status
            booking.updated_at = datetime.utcnow()
            updated_bookings.append(booking)
            
            # Create status history record for each booking
            # (implement BookingStatusHistoryModel first)
        
        db.commit()
        
        # Return updated bookings with full details
        return [self.get_booking_by_id(db, booking.id) for booking in updated_bookings]
    
    def get_booking_status_history(self, db: Session, booking_id: UUID):
        """Get booking status change history"""
        # This requires BookingStatusHistoryModel to be implemented
        # return db.query(BookingStatusHistoryModel).filter(
        #     BookingStatusHistoryModel.booking_id == booking_id
        # ).order_by(desc(Booking