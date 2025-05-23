"""
Service for admin order management
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func, desc

from app.models.order import OrderModel, OrderStatus, OrderItemModel
from app.models.user import UserModel
from app.models.coffee_shop import CoffeeShopModel
from app.models.coffee_menu import CoffeeMenuModel
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
            if order.order_items:
                coffee_shop_name = order.order_items[0].coffee.coffee_shop.name
            
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
                user_name=order.user.full_name,
                user_email=order.user.email,
                coffee_shop_id=order.order_items[0].coffee.coffee_shop_id if order.order_items else None,
                coffee_shop_name=coffee_shop_name,
                items_count=len(order.order_items),
                items_summary=items_summary,
                payment_status="Paid" if order.paid_by_user_id else "Unpaid",
                paid_by_user_id=order.paid_by_user_id,
                paid_by_user_name=order.paid_by_user.full_name if order.paid_by_user else None,
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
        notes: Optional[str] = None
    ):
        """Update order status and create history record"""
        order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
        if not order:
            return None
        
        old_status = order.status
        order.status = new_status
        order.updated_at = datetime.utcnow()
        
        # Create status history record (you'll need to create this model)
        # status_history = OrderStatusHistoryModel(
        #     order_id=order_id,
        #     old_status=old_status,
        #     new_status=new_status,
        #     changed_by_user_id=changed_by_user_id,
        #     notes=notes,
        #     changed_at=datetime.utcnow()
        # )
        # db.add(status_history)
        
        db.commit()
        db.refresh(order)
        
        return self.get_order_by_id(db, order_id)
    
    def bulk_update_order_status(
        self,
        db: Session,
        order_ids: List[UUID],
        new_status: OrderStatus,
        notes: Optional[str] = None
    ):
        """Bulk update order statuses"""
        orders = db.query(OrderModel).filter(OrderModel.id.in_(order_ids)).all()
        updated_orders = []
        
        for order in orders:
            old_status = order.status
            order.status = new_status
            order.updated_at = datetime.utcnow()
            updated_orders.append(order)
            
            # Create status history record for each order
            # (implement OrderStatusHistoryModel first)
        
        db.commit()
        
        # Return updated orders with full details
        return [self.get_order_by_id(db, order.id) for order in updated_orders]
    
    def get_order_status_history(self, db: Session, order_id: UUID):
        """Get order status change history"""
        # This requires OrderStatusHistoryModel to be implemented
        # return db.query(OrderStatusHistoryModel).filter(
        #     OrderStatusHistoryModel.order_id == order_id
        # ).order_by(desc(OrderStatusHistoryModel.changed_at)).all()
        return []  # Placeholder
    
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
    
    def get_today_orders_summary(self, db: Session, coffee_shop_id: Optional[UUID] = None):
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
        
        total_orders = len(orders)
        pending_orders = len([o for o in orders if o.status == OrderStatus.PENDING])
        processing_orders = len([o for o in orders if o.status in [OrderStatus.CONFIRMED, OrderStatus.PREPARING]])
        completed_orders = len([o for o in orders if o.status == OrderStatus.COMPLETED])
        cancelled_orders = len([o for o in orders if o.status == OrderStatus.CANCELLED])
        
        total_revenue = sum(o.total_price for o in orders if o.status != OrderStatus.CANCELLED)
        average_order_value = total_revenue // total_orders if total_orders > 0 else 0
        
        return TodayOrdersSummary(
            total_orders=total_orders,
            pending_orders=pending_orders,
            processing_orders=processing_orders,
            completed_orders=completed_orders,
            cancelled_orders=cancelled_orders,
            total_revenue=total_revenue,
            average_order_value=average_order_value
        )

# Create instance
admin_order_service = AdminOrderService()