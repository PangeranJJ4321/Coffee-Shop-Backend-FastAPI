"""
Schemas for admin analytics and statistics
"""
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from pydantic import BaseModel

class DashboardSummaryResponse(BaseModel):
    """Main dashboard summary statistics"""
    total_revenue_today: int
    total_revenue_this_month: int
    total_orders_today: int
    total_orders_this_month: int
    total_bookings_today: int
    total_bookings_this_month: int
    active_users_today: int
    active_users_this_month: int
    pending_orders_count: int
    upcoming_bookings_count: int
    top_selling_item_today: Optional[str] = None
    revenue_growth_percentage: float  # Month over month
    order_growth_percentage: float    # Month over month

class SalesDataPoint(BaseModel):
    date: str
    total_sales: int
    order_count: int
    average_order_value: int

class SalesAnalyticsResponse(BaseModel):
    total_revenue: int
    total_orders: int
    average_order_value: int
    growth_percentage: float
    sales_data: List[SalesDataPoint]
    peak_sales_day: Optional[str] = None
    peak_sales_amount: int

class RevenueDataPoint(BaseModel):
    period: str
    revenue: int
    profit_margin: float
    cost: int

class RevenueAnalyticsResponse(BaseModel):
    total_revenue: int
    total_profit: int
    average_profit_margin: float
    revenue_data: List[RevenueDataPoint]
    highest_revenue_period: str
    lowest_revenue_period: str

class OrderAnalyticsResponse(BaseModel):
    total_orders: int
    completed_orders: int
    cancelled_orders: int
    pending_orders: int
    completion_rate: float
    cancellation_rate: float
    average_preparation_time: float  # in minutes
    peak_order_hour: int
    order_status_distribution: Dict[str, int]

class UserAnalyticsResponse(BaseModel):
    total_users: int
    new_users_this_period: int
    active_users: int  # Users with orders in period
    returning_customers: int
    customer_retention_rate: float
    average_orders_per_user: float
    top_customers: List[Dict[str, Any]]  # [{name, email, total_orders, total_spent}]

class CoffeeShopPerformance(BaseModel):
    coffee_shop_id: str
    coffee_shop_name: str
    total_revenue: int
    total_orders: int
    average_order_value: int
    customer_satisfaction: Optional[float] = None
    performance_rank: int

class CoffeeShopAnalyticsResponse(BaseModel):
    total_coffee_shops: int
    top_performing_shops: List[CoffeeShopPerformance]
    total_revenue_all_shops: int
    average_revenue_per_shop: int

class PopularItem(BaseModel):
    coffee_id: str
    coffee_name: str
    total_quantity: int
    total_revenue: int
    order_frequency: int
    rank: int

class PopularItemsResponse(BaseModel):
    popular_items: List[PopularItem]
    total_items_analyzed: int
    analysis_period: str

class CustomerSegment(BaseModel):
    segment_name: str
    customer_count: int
    average_order_value: int
    total_revenue: int
    percentage_of_total: float

class CustomerBehaviorResponse(BaseModel):
    customer_segments: List[CustomerSegment]
    peak_ordering_hours: List[int]
    average_session_duration: float  # in minutes
    repeat_customer_rate: float
    new_vs_returning_ratio: Dict[str, float]
    popular_payment_methods: Dict[str, int]

class DateRangeAnalytics(BaseModel):
    """Comprehensive analytics for a specific date range"""
    period_start: date
    period_end: date
    total_revenue: int
    total_orders: int
    total_bookings: int
    unique_customers: int
    
    # Daily breakdown
    daily_revenue: List[SalesDataPoint]
    
    # Performance metrics
    average_order_value: int
    customer_acquisition_cost: float
    customer_lifetime_value: float
    
    # Trends
    revenue_trend: str  # "increasing", "decreasing", "stable"
    order_trend: str
    customer_trend: str
    
    # Comparisons
    previous_period_comparison: Dict[str, float]  # percentage changes
    
    # Top performers
    top_selling_items: List[PopularItem]
    top_customers: List[Dict[str, Any]]
    best_performing_days: List[str]