"""
Service for admin order management
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc

from app.models.order import OrderModel, OrderStatus, OrderItemModel
from app.models.coffee import CoffeeMenuModel
from app.models.order_status_history import OrderStatusHistoryModel
from app.schemas.admin_order_schema import (
    OrderManagementResponse,
    OrderStatusHistoryResponse,
    TodayOrdersSummary
)

class AdminOrderService:
    def get_all_orders(
        self, 
        db: Session, 
        status: Optional[OrderStatus] = None,
        coffee_shop_id: Optional[UUID] = None,
        user_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[OrderManagementResponse]:
        """Get all orders with filtering"""
        query = db.query(OrderModel).options(
            joinedload(OrderModel.user),
            joinedload(OrderModel.order_items).joinedload(OrderItemModel.coffee),
            joinedload(OrderModel.paid_by_user)
        )
        
        # Apply filters
        if status:
            query = query.filter(OrderModel.status == status)
        if coffee_shop_id:
            query = query.join(OrderItemModel).join(CoffeeMenuModel).filter(
                CoffeeMenuModel.coffee_shop_id == coffee_shop_id
            )
        if user_id:
            query = query.filter(OrderModel.user_id == user_id)
        
        orders = query.order_by(desc(OrderModel.created_at)).offset(skip).limit(limit).all()
        
        # Convert to response format
        result = []
        for order in orders:
            # Get coffee shop info from first order item
            coffee_shop_name = "Unknown"
            coffee_shop_id_val = None
            if order.order_items:
                coffee_shop_name = order.order_items[0].coffee.coffee_shop.name
                coffee_shop_id_val = order.order_items[0].coffee.coffee_shop_id
            
            # Create items summary
            items_summary = ", ".join([
                f"{item.quantity}x {item.coffee.name}" 
                for item in order.order_items[:3]  # Show first 3 items
            ])
            if len(order.order_items) > 3:
                items_summary += f" (+{len(order.order_items) - 3} more)"
            
            result.append(OrderManagementResponse(
                id=order.id,
                order_id=order.order_id,
                status=order.status,
                total_price=order.total_price,
                ordered_at=order.ordered_at,
                user_id=order.user_id,
                user_name=order.user.name,
                user_email=order.user.email,
                coffee_shop_id=coffee_shop_id_val,
                coffee_shop_name=coffee_shop_name,
                items_count=len(order.order_items),
                items_summary=items_summary,
                payment_status="Paid" if order.paid_by_user_id else "Unpaid",
                paid_by_user_id=order.paid_by_user_id,
                paid_by_user_name=order.paid_by_user.name if order.paid_by_user else None,
                booking_id=order.booking_id,
                created_at=order.created_at,
                updated_at=order.updated_at
            ))
        
        return result
    
    def get_order_by_id(self, db: Session, order_id: UUID):
        """Get order by ID with all details"""
        return db.query(OrderModel).options(
            joinedload(OrderModel.user),
            joinedload(OrderModel.order_items).joinedload(OrderItemModel.coffee),
            joinedload(OrderModel.paid_by_user)
        ).filter(OrderModel.id == order_id).first()
    
    def update_order_status(
        self, 
        db: Session, 
        order_id: UUID, 
        new_status: OrderStatus,
        notes: Optional[str] = None,
        changed_by_user_id: Optional[UUID] = None
    ):
        """Update order status and create history record"""
        order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
        if not order:
            return None
        
        old_status = order.status
        order.status = new_status
        order.updated_at = datetime.utcnow()
        
        # TODO: Create status history record when OrderStatusHistoryModel is implemented
        if changed_by_user_id:
            status_history = OrderStatusHistoryModel(
                order_id=order_id,
                old_status=old_status,
                new_status=new_status,
                changed_by_user_id=changed_by_user_id,
                notes=notes,
                changed_at=datetime.utcnow()
            )
            db.add(status_history)
        
        db.commit()
        db.refresh(order)
        
        return order
    
    def bulk_update_order_status(
        self,
        db: Session,
        order_ids: List[UUID],
        new_status: OrderStatus,
        notes: Optional[str] = None,
        changed_by_user_id: Optional[UUID] = None
    ):
        """Bulk update order statuses"""
        orders = db.query(OrderModel).filter(OrderModel.id.in_(order_ids)).all()
        updated_orders = []
        
        for order in orders:
            old_status = order.status
            order.status = new_status
            order.updated_at = datetime.utcnow()
            updated_orders.append(order)
            
            # TODO: Create status history record for each order when model is implemented
            if changed_by_user_id:
                status_history = OrderStatusHistoryModel(
                    order_id=order.id,
                    old_status=old_status,
                    new_status=new_status,
                    changed_by_user_id=changed_by_user_id,
                    notes=notes,
                    changed_at=datetime.utcnow()
                )
                db.add(status_history)
        
        db.commit()
        
        # Return updated orders with full details (convert to OrderManagementResponse)
        result = []
        for order in updated_orders:
            # Refresh order to get related data
            db.refresh(order)
            
            # Get coffee shop info
            coffee_shop_name = "Unknown"
            coffee_shop_id_val = None
            if order.order_items:
                coffee_shop_name = order.order_items[0].coffee.coffee_shop.name
                coffee_shop_id_val = order.order_items[0].coffee.coffee_shop_id
            
            # Create items summary
            items_summary = ", ".join([
                f"{item.quantity}x {item.coffee.name}" 
                for item in order.order_items[:3]
            ])
            if len(order.order_items) > 3:
                items_summary += f" (+{len(order.order_items) - 3} more)"
            
            result.append(OrderManagementResponse(
                id=order.id,
                order_id=order.order_id,
                status=order.status,
                total_price=order.total_price,
                ordered_at=order.ordered_at,
                user_id=order.user_id,
                user_name=order.user.name,
                user_email=order.user.email,
                coffee_shop_id=coffee_shop_id_val,
                coffee_shop_name=coffee_shop_name,
                items_count=len(order.order_items),
                items_summary=items_summary,
                payment_status="Paid" if order.paid_by_user_id else "Unpaid",
                paid_by_user_id=order.paid_by_user_id,
                paid_by_user_name=order.paid_by_user.name if order.paid_by_user else None,
                booking_id=order.booking_id,
                created_at=order.created_at,
                updated_at=order.updated_at
            ))
        
        return result
    
    def get_order_status_history(self, db: Session, order_id: UUID) -> List[OrderStatusHistoryResponse]:
        """Get order status change history"""
        # TODO: This requires OrderStatusHistoryModel to be implemented
        # When implemented, use this query:
        # history = db.query(OrderStatusHistoryModel).options(
        #     joinedload(OrderStatusHistoryModel.changed_by_user)
        # ).filter(
        #     OrderStatusHistoryModel.order_id == order_id
        # ).order_by(desc(OrderStatusHistoryModel.changed_at)).all()
        # 
        # return [OrderStatusHistoryResponse(
        #     id=h.id,
        #     order_id=h.order_id,
        #     old_status=h.old_status,
        #     new_status=h.new_status,
        #     changed_by_user_id=h.changed_by_user_id,
        #     changed_by_user_name=h.changed_by_user.name,
        #     notes=h.notes,
        #     changed_at=h.changed_at
        # ) for h in history]
        
        # Check if order exists first
        order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
        if not order:
            return None
            
        return []  # Placeholder until model is implemented
    
    def get_pending_orders_count(self, db: Session, coffee_shop_id: Optional[UUID] = None) -> int:
        """Get count of pending orders"""
        query = db.query(OrderModel).filter(
            OrderModel.status.in_([OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.PREPARING])
        )
        
        if coffee_shop_id:
            query = query.join(OrderItemModel).join(CoffeeMenuModel).filter(
                CoffeeMenuModel.coffee_shop_id == coffee_shop_id
            )
        
        return query.count()
    
    def get_today_orders_summary(self, db: Session, coffee_shop_id: Optional[UUID] = None) -> TodayOrdersSummary:
        """Get today's orders summary"""
        today = date.today()
        query = db.query(OrderModel).filter(
            func.date(OrderModel.ordered_at) == today
        )
        
        if coffee_shop_id:
            query = query.join(OrderItemModel).join(CoffeeMenuModel).filter(
                CoffeeMenuModel.coffee_shop_id == coffee_shop_id
            )
        
        orders = query.all()
        
        # Calculate summary statistics
        total_orders = len(orders)
        total_revenue = sum(order.total_price for order in orders if order.total_price)
        
        # Count orders by status
        status_counts = {
            'pending': 0,
            'confirmed': 0,
            'preparing': 0,
            'ready': 0,
            'completed': 0,
            'cancelled': 0
        }
        
        for order in orders:
            if order.status == OrderStatus.PENDING:
                status_counts['pending'] += 1
            elif order.status == OrderStatus.CONFIRMED:
                status_counts['confirmed'] += 1
            elif order.status == OrderStatus.PREPARING:
                status_counts['preparing'] += 1
            elif order.status == OrderStatus.READY:
                status_counts['ready'] += 1
            elif order.status == OrderStatus.COMPLETED:
                status_counts['completed'] += 1
            elif order.status == OrderStatus.CANCELLED:
                status_counts['cancelled'] += 1
        
        # Get hourly distribution (last 24 hours)
        hourly_orders = {}
        for hour in range(24):
            hourly_orders[f"{hour:02d}:00"] = 0
        
        for order in orders:
            hour = order.ordered_at.hour
            hourly_orders[f"{hour:02d}:00"] += 1
        
        # Get top coffee items ordered today
        coffee_items = {}
        for order in orders:
            for item in order.order_items:
                coffee_name = item.coffee.name
                if coffee_name in coffee_items:
                    coffee_items[coffee_name] += item.quantity
                else:
                    coffee_items[coffee_name] = item.quantity
        
        # Sort and get top 5
        top_coffee_items = sorted(
            coffee_items.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return TodayOrdersSummary(
            date=today,
            total_orders=total_orders,
            total_revenue=total_revenue,
            status_breakdown=status_counts,
            hourly_distribution=hourly_orders,
            top_coffee_items=[
                {"name": name, "quantity": quantity} 
                for name, quantity in top_coffee_items
            ],
            average_order_value=total_revenue / total_orders if total_orders > 0 else 0,
            peak_hour=max(hourly_orders.items(), key=lambda x: x[1])[0] if orders else "00:00"
        )
    
    def get_orders_by_date_range(
        self,
        db: Session,
        start_date: date,
        end_date: date,
        coffee_shop_id: Optional[UUID] = None,
        status: Optional[OrderStatus] = None
    ) -> List[OrderManagementResponse]:
        """Get orders within a date range"""
        query = db.query(OrderModel).options(
            joinedload(OrderModel.user),
            joinedload(OrderModel.order_items).joinedload(OrderItemModel.coffee),
            joinedload(OrderModel.paid_by_user)
        ).filter(
            func.date(OrderModel.ordered_at).between(start_date, end_date)
        )
        
        if coffee_shop_id:
            query = query.join(OrderItemModel).join(CoffeeMenuModel).filter(
                CoffeeMenuModel.coffee_shop_id == coffee_shop_id
            )
        
        if status:
            query = query.filter(OrderModel.status == status)
        
        orders = query.order_by(desc(OrderModel.ordered_at)).all()
        
        # Convert to response format using the same logic as get_all_orders
        return self._convert_orders_to_response(orders)
    
    def _convert_orders_to_response(self, orders: List[OrderModel]) -> List[OrderManagementResponse]:
        """Helper method to convert OrderModel list to OrderManagementResponse list"""
        result = []
        for order in orders:
            # Get coffee shop info from first order item
            coffee_shop_name = "Unknown"
            coffee_shop_id_val = None
            if order.order_items:
                coffee_shop_name = order.order_items[0].coffee.coffee_shop.name
                coffee_shop_id_val = order.order_items[0].coffee.coffee_shop_id
            
            # Create items summary
            items_summary = ", ".join([
                f"{item.quantity}x {item.coffee.name}" 
                for item in order.order_items[:3]  # Show first 3 items
            ])
            if len(order.order_items) > 3:
                items_summary += f" (+{len(order.order_items) - 3} more)"
            
            result.append(OrderManagementResponse(
                id=order.id,
                order_id=order.order_id,
                status=order.status,
                total_price=order.total_price,
                ordered_at=order.ordered_at,
                user_id=order.user_id,
                user_name=order.user.name,
                user_email=order.user.email,
                coffee_shop_id=coffee_shop_id_val,
                coffee_shop_name=coffee_shop_name,
                items_count=len(order.order_items),
                items_summary=items_summary,
                payment_status="Paid" if order.paid_by_user_id else "Unpaid",
                paid_by_user_id=order.paid_by_user_id,
                paid_by_user_name=order.paid_by_user.name if order.paid_by_user else None,
                booking_id=order.booking_id,
                created_at=order.created_at,
                updated_at=order.updated_at
            ))
        
        return result

# Create singleton instance
admin_order_service = AdminOrderService()