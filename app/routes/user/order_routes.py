# app/routes/user/order_routes.py - Updated with payable orders endpoint. dikit lagi ahaha

"""
Routes for user coffee orders - Updated with pay for others functionality
"""
from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import UserModel
from app.schemas.order_schema import (
    OrderCreate,
    OrderResponse,
    OrderWithItemsResponse,
    OrderFilterParams,
    PayableOrderResponse
)
from app.services.order_service import order_service
from app.utils.security import get_current_user

router = APIRouter(prefix="/orders", tags=["User Orders"])

@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Create a new coffee order"""
    return order_service.create_order(db, order_data, current_user.id)

@router.get("/", response_model=List[OrderResponse])
async def get_user_orders(
    params: OrderFilterParams = Depends(),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get all orders for the current user with optional filtering"""
    return order_service.get_user_orders(db, current_user.id, params)

@router.get("/payable", response_model=List[PayableOrderResponse])  
async def get_payable_orders(
    limit: int = Query(default=20, le=100, description="Maximum number of orders to return"),
    offset: int = Query(default=0, ge=0, description="Number of orders to skip"),
    coffee_shop_id: UUID = Query(None, description="Filter by coffee shop"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get orders that can be paid by others (excluding current user's orders)"""
    return order_service.get_payable_orders(db, current_user.id, limit, offset, coffee_shop_id)

@router.get("/{order_id}", response_model=OrderWithItemsResponse)
async def get_order_details(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get detailed information about a specific order"""
    order = order_service.get_order_by_id(db, order_id, current_user.id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order

@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(
    order_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Cancel an order (only allowed for pending orders)"""
    success = order_service.cancel_order(db, order_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to cancel order. Order might not be in pending state or not found."
        )
    return {"detail": "Order cancelled successfully"}