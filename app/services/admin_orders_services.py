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
                user_name=order.user.full_name,
                user_email=order.user.email,
                coffee_shop_id=coffee_shop_id_val,
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
        # Example implementation:
        # if changed_by_user_id:
        #     status_history = OrderStatusHistoryModel(
        #         order_id=order_id,
        #         old_status=old_status,
        #         new_status=new_status,
        #         changed_by_user_id=changed_by_user_id,
        #         notes=notes,
        #         changed_at=datetime.utcnow()
        #     )
        #     db.add(status_history)
        
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
            # if changed_by_user_id:
            #     status_history = OrderStatusHistoryModel(
            #         order_id=order.id,
            #         old_status=old_status,
            #         new_status=new_status,
            #         changed_by_user_id=changed_by_user_id,
            #         notes=notes,
            #         changed_at=datetime.utcnow()
            #     )
            #     db.add(status_history)
        
        db.commit()
        
        # Return updated orders with full details (convert to OrderManagementResponse)
        result = []
        for order in updated_orders:
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
                user_name=order.user.full_name,
                user_email=order.user.email,
                coffee_shop_id=coffee_shop_id_val,
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
        #     changed_by_user_name=h.changed_by_user.full_name,
        #     notes=h.notes,
        #     changed_at=h.changed_at
        # ) for h in history]
        
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
            query = query.join(OrderItem