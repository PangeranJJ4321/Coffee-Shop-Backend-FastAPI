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
        notes: Optional[str] = None,
        changed_by_user_id: Optional[UUID] = None
    ):
        """Update booking status and create history record"""
        booking = db.query(BookingModel).filter(BookingModel.id == booking_id).first()
        if not booking:
            return None
        
        old_status = booking.status
        booking.status = new_status
        booking.updated_at = datetime.utcnow()
        
        # TODO: Create status history record when BookingStatusHistoryModel is implemented
        # Example implementation:
        # if changed_by_user_id:
        #     status_history = BookingStatusHistoryModel(
        #         booking_id=booking_id,
        #         old_status=old_status,
        #         new_status=new_status,
        #         changed_by_user_id=changed_by_user_id,
        #         notes=notes,
        #         changed_at=datetime.utcnow()
        #     )
        #     db.add(status_history)
        
        db.commit()
        db.refresh(booking)
        
        return self.get_booking_by_id(db, booking_id)
    
    def bulk_update_booking_status(
        self,
        db: Session,
        booking_ids: List[UUID],
        new_status: BookingStatus,
        notes: Optional[str] = None,
        changed_by_user_id: Optional[UUID] = None
    ):
        """Bulk update booking statuses"""
        bookings = db.query(BookingModel).filter(BookingModel.id.in_(booking_ids)).all()
        updated_bookings = []
        
        for booking in bookings:
            old_status = booking.status
            booking.status = new_status
            booking.updated_at = datetime.utcnow()
            updated_bookings.append(booking)
            
            # TODO: Create status history record for each booking when model is implemented
            # if changed_by_user_id:
            #     status_history = BookingStatusHistoryModel(
            #         booking_id=booking.id,
            #         old_status=old_status,
            #         new_status=new_status,
            #         changed_by_user_id=changed_by_user_id,
            #         notes=notes,
            #         changed_at=datetime.utcnow()
            #     )
            #     db.add(status_history)
        
        db.commit()
        
        # Return updated bookings with full details
        return [self.get_booking_by_id(db, booking.id) for booking in updated_bookings]
    
    def get_booking_status_history(self, db: Session, booking_id: UUID) -> List[BookingStatusHistoryResponse]:
        """Get booking status change history"""
        # TODO: This requires BookingStatusHistoryModel to be implemented
        # When implemented, use this query:
        # history = db.query(BookingStatusHistoryModel).options(
        #     joinedload(BookingStatusHistoryModel.changed_by_user)
        # ).filter(
        #     BookingStatusHistoryModel.booking_id == booking_id
        # ).order_by(desc(BookingStatusHistoryModel.changed_at)).all()
        # 
        # return [BookingStatusHistoryResponse(
        #     id=h.id,
        #     booking_id=h.booking_id,
        #     old_status=h.old_status,
        #     new_status=h.new_status,
        #     changed_by_user_id=h.changed_by_user_id,
        #     changed_by_user_name=h.changed_by_user.full_name,
        #     notes=h.notes,
        #     changed_at=h.changed_at
        # ) for h in history]
        
        return []  # Placeholder until model is implemented
    
    def get_today_bookings_summary(self, db: Session, coffee_shop_id: Optional[UUID] = None) -> TodayBookingsSummary:
        """Get today's bookings summary"""
        today = date.today()
        query = db.query(BookingModel).filter(
            func.date(BookingModel.booking_date) == today
        )
        
        if coffee_shop_id:
            query = query.filter(BookingModel.coffee_shop_id == coffee_shop_id)
        
        bookings = query.all()
        
        total_bookings = len(bookings)
        confirmed_bookings = len([b for b in bookings if b.status == BookingStatus.CONFIRMED])
        pending_bookings = len([b for b in bookings if b.status == BookingStatus.PENDING])
        cancelled_bookings = len([b for b in bookings if b.status == BookingStatus.CANCELLED])
        completed_bookings = len([b for b in bookings if b.status == BookingStatus.COMPLETED])
        
        # Calculate total guests
        total_guests = sum(b.guest_count for b in bookings if b.status != BookingStatus.CANCELLED)
        
        # Find peak time slot (group by hour)
        peak_time_slot = None
        if bookings:
            from collections import Counter
            time_slots = [b.booking_date.hour for b in bookings if b.status in [BookingStatus.CONFIRMED, BookingStatus.COMPLETED]]
            if time_slots:
                most_common_hour = Counter(time_slots).most_common(1)[0][0]
                peak_time_slot = f"{most_common_hour:02d}:00-{most_common_hour+1:02d}:00"
        
        # Calculate occupancy rate (this would need table capacity info)
        # For now, we'll use a simple calculation based on confirmed bookings
        occupancy_rate = (confirmed_bookings + completed_bookings) / max(total_bookings, 1) * 100 if total_bookings > 0 else 0
        
        return TodayBookingsSummary(
            total_bookings=total_bookings,
            confirmed_bookings=confirmed_bookings,
            pending_bookings=pending_bookings,
            cancelled_bookings=cancelled_bookings,
            completed_bookings=completed_bookings,
            total_guests=total_guests,
            peak_time_slot=peak_time_slot,
            occupancy_rate=occupancy_rate
        )
    
    def get_upcoming_bookings_count(self, db: Session, coffee_shop_id: Optional[UUID] = None) -> int:
        """Get count of upcoming bookings (today and future)"""
        now = datetime.utcnow()
        query = db.query(BookingModel).filter(
            BookingModel.booking_date >= now,
            BookingModel.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED])
        )
        
        if coffee_shop_id:
            query = query.filter(BookingModel.coffee_shop_id == coffee_shop_id)
        
        return query.count()
    
    def get_bookings_by_date_range(
        self, 
        db: Session, 
        start_date: date, 
        end_date: date,
        coffee_shop_id: Optional[UUID] = None,
        status: Optional[BookingStatus] = None
    ) -> List[BookingManagementResponse]:
        """Get bookings within a date range"""
        query = db.query(BookingModel).options(
            joinedload(BookingModel.user),
            joinedload(BookingModel.coffee_shop),
            joinedload(BookingModel.booking_tables).joinedload(BookingTableModel.table)
        ).filter(
            func.date(BookingModel.booking_date) >= start_date,
            func.date(BookingModel.booking_date) <= end_date
        )
        
        if coffee_shop_id:
            query = query.filter(BookingModel.coffee_shop_id == coffee_shop_id)
        if status:
            query = query.filter(BookingModel.status == status)
        
        bookings = query.order_by(BookingModel.booking_date).all()
        
        # Convert to response format
        result = []
        for booking in bookings:
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
    
    def get_bookings_statistics(self, db: Session, coffee_shop_id: Optional[UUID] = None):
        """Get booking statistics for analytics"""
        query = db.query(BookingModel)
        
        if coffee_shop_id:
            query = query.filter(BookingModel.coffee_shop_id == coffee_shop_id)
        
        # Get all bookings
        all_bookings = query.all()
        
        # Calculate statistics
        total_bookings = len(all_bookings)
        status_distribution = {}
        
        for status in BookingStatus:
            count = len([b for b in all_bookings if b.status == status])
            status_distribution[status.value] = count
        
        # Monthly statistics
        today = date.today()
        this_month_start = today.replace(day=1)
        this_month_bookings = [
            b for b in all_bookings 
            if b.created_at.date() >= this_month_start
        ]
        
        # Calculate average booking lead time (days between creation and booking date)
        lead_times = [
            (b.booking_date.date() - b.created_at.date()).days 
            for b in all_bookings 
            if b.booking_date.date() > b.created_at.date()
        ]
        average_lead_time = sum(lead_times) / len(lead_times) if lead_times else 0
        
        return {
            "total_bookings": total_bookings,
            "this_month_bookings": len(this_month_bookings),
            "status_distribution": status_distribution,
            "average_lead_time_days": round(average_lead_time, 2),
            "completion_rate": (status_distribution.get("COMPLETED", 0) / max(total_bookings, 1)) * 100,
            "cancellation_rate": (status_distribution.get("CANCELLED", 0) / max(total_bookings, 1)) * 100
        }

# Create instance
admin_booking_service = AdminBookingService()