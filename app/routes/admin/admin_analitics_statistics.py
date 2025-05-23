"""
Controller for admin analytics and statistics
"""
from typing import Optional
from uuid import UUID
from datetime import date, datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import UserModel
from app.schemas.admin_analytics_schema import (
    SalesAnalyticsResponse,
    OrderAnalyticsResponse,
    UserAnalyticsResponse,
    CoffeeShopAnalyticsResponse,
    DashboardSummaryResponse,
    RevenueAnalyticsResponse,
    PopularItemsResponse,
    CustomerBehaviorResponse,
    DateRangeAnalytics
)
from app.services.admin_analytics_service import admin_analytics_service
from app.utils.security import get_current_admin_user

router = APIRouter(prefix="/analytics", tags=["Admin ~ Analytics & Statistics"])

@router.get("/dashboard/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    coffee_shop_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get dashboard summary statistics (Admin only)"""
    return admin_analytics_service.get_dashboard_summary(db, coffee_shop_id)

@router.get("/sales", response_model=SalesAnalyticsResponse)
async def get_sales_analytics(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    coffee_shop_id: Optional[UUID] = Query(None),
    group_by: str = Query("day", regex="^(day|week|month)$"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get sales analytics with date range and grouping (Admin only)"""
    return admin_analytics_service.get_sales_analytics(
        db, start_date, end_date, coffee_shop_id, group_by
    )

@router.get("/revenue", response_model=RevenueAnalyticsResponse)
async def get_revenue_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    coffee_shop_id: Optional[UUID] = Query(None),
    group_by: str = Query("day", regex="^(day|week|month)$"),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get revenue analytics (Admin only)"""
    return admin_analytics_service.get_revenue_analytics(
        db, start_date, end_date, coffee_shop_id, group_by
    )

@router.get("/orders", response_model=OrderAnalyticsResponse)
async def get_order_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    coffee_shop_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get order analytics (Admin only)"""
    return admin_analytics_service.get_order_analytics(
        db, start_date, end_date, coffee_shop_id
    )

@router.get("/users", response_model=UserAnalyticsResponse)
async def get_user_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    coffee_shop_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get user analytics (Admin only)"""
    return admin_analytics_service.get_user_analytics(
        db, start_date, end_date, coffee_shop_id
    )

@router.get("/coffee-shops", response_model=CoffeeShopAnalyticsResponse)
async def get_coffee_shop_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get coffee shop performance analytics (Admin only)"""
    return admin_analytics_service.get_coffee_shop_analytics(
        db, start_date, end_date
    )

@router.get("/popular-items", response_model=PopularItemsResponse)
async def get_popular_items(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    coffee_shop_id: Optional[UUID] = Query(None),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get popular menu items analytics (Admin only)"""
    return admin_analytics_service.get_popular_items(
        db, start_date, end_date, coffee_shop_id, limit
    )

@router.get("/customer-behavior", response_model=CustomerBehaviorResponse)
async def get_customer_behavior_analytics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    coffee_shop_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get customer behavior analytics (Admin only)"""
    return admin_analytics_service.get_customer_behavior_analytics(
        db, start_date, end_date, coffee_shop_id
    )

@router.get("/date-range", response_model=DateRangeAnalytics)
async def get_date_range_analytics(
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    coffee_shop_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Get comprehensive analytics for a specific date range (Admin only)"""
    return admin_analytics_service.get_date_range_analytics(
        db, start_date, end_date, coffee_shop_id
    )

@router.get("/export/csv")
async def export_analytics_csv(
    report_type: str = Query(..., regex="^(sales|orders|users|revenue)$"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    coffee_shop_id: Optional[UUID] = Query(None),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_admin_user)
):
    """Export analytics data as CSV (Admin only)"""
    return admin_analytics_service.export_analytics_csv(
        db, report_type, start_date, end_date, coffee_shop_id
    )