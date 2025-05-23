"""
Controller for admin order management
"""
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import UserModel
from app.schemas.order_schema import OrderWithItemsResponse, OrderFilterParams
from app.schemas.admin_order_schema import (
    OrderStatusUpdate,
    OrderManagementResponse,
    OrderStatusHistoryResponse,
    BulkOrderStatusUpdate
)
from app.services.admin_order_service import admin_order_service
from app.services.notification_service import notification_service
from app.utils.security import get_current_admin_user
from app.models.order import OrderStatus

router = APIRouter(prefix="/order-management", tags=["Admin ~ Order Management"])

@router.get("/orders", response_model=List[OrderManagementResponse])
async def get_all_orders(
    status: Optional[OrderStatus] = Query(None, description="Filter by order status"),
    coffee_shop_id: Optional[UUID] = Query(None, description="Filter by coffee shop"),
    user_id: Optional[UUID] = Query(None, description="Filter by user"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get all orders with filtering options (Admin only)"""
    return admin_order_service.get_all_orders(
        db, status=status, coffee_shop_id=coffee_shop_id, 
        user_id=user_id, skip=skip, limit=limit
    )

@router.get("/orders/{order_id}", response_model=OrderWithItemsResponse)
async def get_order_details(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get detailed order information (Admin only)"""
    order = admin_order_service.get_order_by_id(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order

@router.put("/orders/{order_id}/status", response_model=OrderManagementResponse)
async def update_order_status(
    order_id: UUID,
    status_update: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Update order status and send notification (Admin only)"""
    # Update order status
    updated_order = admin_order_service.update_order_status(
        db, order_id, status_update.status, status_update.notes
    )
    
    if not updated_order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Send notification to user
    try:
        await notification_service.send_order_status_notification(
            db, order_id, status_update.status, current_user.id
        )
    except Exception as e:
        # Log error but don't fail the request
        print(f"Failed to send notification: {str(e)}")
    
    return updated_order

@router.get("/orders/{order_id}/status-history", response_model=List[OrderStatusHistoryResponse])
async def get_order_status_history(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get order status change history (Admin only)"""
    history = admin_order_service.get_order_status_history(db, order_id)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found or no status history available"
        )
    return history

@router.put("/orders/bulk-status-update", response_model=List[OrderManagementResponse])
async def bulk_update_order_status(
    bulk_update: BulkOrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Bulk update order statuses (Admin only)"""
    updated_orders = admin_order_service.bulk_update_order_status(
        db, bulk_update.order_ids, bulk_update.status, bulk_update.notes
    )
    
    # Send notifications for each updated order
    for order in updated_orders:
        try:
            await notification_service.send_order_status_notification(
                db, order.id, bulk_update.status, current_user.id
            )
        except Exception as e:
            print(f"Failed to send notification for order {order.id}: {str(e)}")
    
    return updated_orders

@router.get("/orders/pending/count")
async def get_pending_orders_count(
    coffee_shop_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get count of pending orders (Admin only)"""
    count = admin_order_service.get_pending_orders_count(db, coffee_shop_id)
    return {"pending_orders_count": count}

@router.get("/orders/today/summary")
async def get_today_orders_summary(
    coffee_shop_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get today's orders summary (Admin only)"""
    summary = admin_order_service.get_today_orders_summary(db, coffee_shop_id)
    return summary