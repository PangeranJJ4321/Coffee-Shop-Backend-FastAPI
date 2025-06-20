from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, extract, and_, or_, distinct, cast
from sqlalchemy.types import Date

# Import semua model yang relevan
from app.models.user import RoleModel, UserModel, Role
from app.models.order import OrderModel, OrderItemModel, OrderStatus, TransactionModel
from app.models.coffee import CoffeeShopModel, CoffeeMenuModel, VariantModel, CoffeeVariantModel
from app.models.booking import BookingModel, BookingStatus, TableModel, BookingTableModel
from app.models.notification import RatingModel 
from app.utils.logger import logger 

from app.schemas.admin_analytics_schema import (
    DashboardSummaryResponse,
    SalesAnalyticsResponse,
    OrderAnalyticsResponse,
    UserAnalyticsResponse,
    CoffeeShopAnalyticsResponse,
    RevenueAnalyticsResponse,
    PopularItemsResponse,
    CustomerBehaviorResponse,
    DateRangeAnalytics,
    SalesDataPoint,
    RevenueDataPoint,
    CoffeeShopPerformance,
    PopularItem,
    CustomerSegment,
)

class AdminAnalyticsService:
    def get_dashboard_summary(self, db: Session, coffee_shop_id: Optional[UUID]) -> DashboardSummaryResponse:
        """
        Mengambil statistik ringkasan dashboard.
        """
        today = date.today()
        this_month_start = today.replace(day=1)
        
        # Base query for orders and bookings, filtered by coffee_shop_id if provided
        orders_base_query = db.query(OrderModel).filter(OrderModel.status == OrderStatus.COMPLETED)
        bookings_base_query = db.query(BookingModel).filter(BookingModel.status == BookingStatus.SUCCESS)

        if coffee_shop_id:
            orders_base_query = orders_base_query.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)
            bookings_base_query = bookings_base_query.join(BookingTableModel, BookingModel.id == BookingTableModel.booking_id)\
                                                    .join(TableModel, BookingTableModel.table_id == TableModel.id)\
                                                    .filter(TableModel.coffee_shop_id == coffee_shop_id)

        # Total Revenue Today
        total_revenue_today = orders_base_query.filter(func.date(OrderModel.ordered_at) == today)\
                                                .with_entities(func.sum(OrderModel.total_price))\
                                                .scalar() or 0

        # Total Revenue This Month
        total_revenue_this_month = orders_base_query.filter(OrderModel.ordered_at >= this_month_start)\
                                                    .with_entities(func.sum(OrderModel.total_price))\
                                                    .scalar() or 0

        # Total Orders Today
        total_orders_today = orders_base_query.filter(func.date(OrderModel.ordered_at) == today).count()

        # Total Orders This Month
        total_orders_this_month = orders_base_query.filter(OrderModel.ordered_at >= this_month_start).count()

        # Total Bookings Today
        total_bookings_today = bookings_base_query.filter(func.date(BookingModel.booking_date) == today).count()

        # Total Bookings This Month
        total_bookings_this_month = bookings_base_query.filter(BookingModel.booking_date >= this_month_start).count()

        # Active Users Today (users who placed an order today)
        active_users_today = db.query(func.count(distinct(OrderModel.user_id)))\
                                .filter(func.date(OrderModel.ordered_at) == today)
        if coffee_shop_id:
            active_users_today = active_users_today.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                    .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                    .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)
        active_users_today = active_users_today.scalar() or 0

        # Active Users This Month (users who placed an order this month)
        active_users_this_month = db.query(func.count(distinct(OrderModel.user_id)))\
                                    .filter(OrderModel.ordered_at >= this_month_start)
        if coffee_shop_id:
            active_users_this_month = active_users_this_month.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                            .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                            .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)
        active_users_this_month = active_users_this_month.scalar() or 0

        total_users_system = db.query(UserModel).count() 

        # Total Menu Items (count all active coffee menu items)
        total_menu_items = db.query(CoffeeMenuModel).filter(CoffeeMenuModel.is_available == True).count()

        # Pending Orders Count
        pending_orders_count = db.query(OrderModel).filter(OrderModel.status == OrderStatus.PENDING)
        if coffee_shop_id:
            pending_orders_count = pending_orders_count.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                        .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                        .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)
        pending_orders_count = pending_orders_count.count()

        # Upcoming Bookings Count (bookings for today or future dates)
        upcoming_bookings_count = db.query(BookingModel).filter(BookingModel.booking_date >= today)\
                                                        .filter(or_(BookingModel.status == BookingStatus.NOCONFIRM, BookingModel.status == BookingStatus.CONFIRM))
        if coffee_shop_id:
            upcoming_bookings_count = upcoming_bookings_count.join(BookingTableModel, BookingModel.id == BookingTableModel.booking_id)\
                                                            .join(TableModel, BookingTableModel.table_id == TableModel.id)\
                                                            .filter(TableModel.coffee_shop_id == coffee_shop_id)
        upcoming_bookings_count = upcoming_bookings_count.count()

        # Top Selling Item Today
        top_selling_item_today_query = db.query(CoffeeMenuModel.name)\
                                        .join(OrderItemModel, CoffeeMenuModel.id == OrderItemModel.coffee_id)\
                                        .join(OrderModel, OrderItemModel.order_id == OrderModel.id)\
                                        .filter(func.date(OrderModel.ordered_at) == today)\
                                        .filter(OrderModel.status == OrderStatus.COMPLETED)
        if coffee_shop_id:
            top_selling_item_today_query = top_selling_item_today_query.filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)
        
        top_selling_item_today = top_selling_item_today_query\
                                .group_by(CoffeeMenuModel.name)\
                                .order_by(func.sum(OrderItemModel.quantity).desc())\
                                .limit(1).scalar()

        # Revenue Growth Percentage (Month over month)
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        last_month_end = this_month_start - timedelta(days=1)

        total_revenue_last_month = orders_base_query.filter(and_(
            OrderModel.ordered_at >= last_month_start,
            OrderModel.ordered_at <= last_month_end
        )).with_entities(func.sum(OrderModel.total_price)).scalar() or 0

        revenue_growth_percentage = 0.0
        if total_revenue_last_month > 0:
            revenue_growth_percentage = ((total_revenue_this_month - total_revenue_last_month) / total_revenue_last_month) * 100
        elif total_revenue_this_month > 0:
            revenue_growth_percentage = 100.0 

        # Order Growth Percentage (Month over month)
        total_orders_last_month = orders_base_query.filter(and_(
            OrderModel.ordered_at >= last_month_start,
            OrderModel.ordered_at <= last_month_end
        )).count()

        order_growth_percentage = 0.0
        if total_orders_last_month > 0:
            order_growth_percentage = ((total_orders_this_month - total_orders_last_month) / total_orders_last_month) * 100
        elif total_orders_this_month > 0:
            order_growth_percentage = 100.0

        users_growth = 0.0 # Placeholder
        menu_growth = 0.0 # Placeholder

        return DashboardSummaryResponse(
            total_revenue_today=total_revenue_today,
            total_revenue_this_month=total_revenue_this_month,
            total_orders_today=total_orders_today,
            total_orders_this_month=total_orders_this_month,
            total_bookings_today=total_bookings_today,
            total_bookings_this_month=total_bookings_this_month,
            active_users_today=active_users_today,
            active_users_this_month=active_users_this_month,
            pending_orders_count=pending_orders_count,
            upcoming_bookings_count=upcoming_bookings_count,
            top_selling_item_today=top_selling_item_today,
            revenue_growth_percentage=round(revenue_growth_percentage, 2),
            order_growth_percentage=round(order_growth_percentage, 2),

            total_users=total_users_system, 
            users_growth=users_growth, 
            total_menu_items=total_menu_items, 
            menu_growth=menu_growth,
        )

    def get_sales_analytics(
        self,
        db: Session,
        start_date: Optional[date],
        end_date: Optional[date],
        coffee_shop_id: Optional[UUID],
        group_by: str,
    ) -> SalesAnalyticsResponse:
        """
        Mengambil analitik penjualan.
        """
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        sales_query_base = db.query(OrderModel).filter(
            and_(
                OrderModel.ordered_at >= start_date,
                OrderModel.ordered_at <= end_date + timedelta(days=1), # Include end_date fully
                OrderModel.status == OrderStatus.COMPLETED
            )
        )
        if coffee_shop_id:
            sales_query_base = sales_query_base.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)

        # Total Revenue, Total Orders, Average Order Value for the period
        total_revenue = sales_query_base.with_entities(func.sum(OrderModel.total_price)).scalar() or 0
        total_orders = sales_query_base.count()
        average_order_value = int(total_revenue / total_orders) if total_orders else 0

        # Sales Data per Period
        sales_data: List[SalesDataPoint] = []
        
        if group_by == "day":
            period_col = func.date(OrderModel.ordered_at).label("period")
        elif group_by == "week":
            period_col = func.to_char(OrderModel.ordered_at, 'YYYY-WW').label("period")
        elif group_by == "month":
            period_col = func.to_char(OrderModel.ordered_at, 'YYYY-MM').label("period")
        else:
            raise ValueError("Invalid group_by parameter. Must be 'day', 'week', or 'month'.")

        sales_data_query = sales_query_base.with_entities(
            period_col,
            func.sum(OrderModel.total_price).label("total_sales"),
            func.count(OrderModel.id).label("order_count")
        ).group_by(period_col).order_by(period_col).all()

        peak_sales_amount = 0
        peak_sales_day: Optional[str] = None

        for row in sales_data_query:
            avg_order_val = int(row.total_sales / row.order_count) if row.order_count else 0
            sales_data.append(SalesDataPoint(
                date=str(row.period),
                total_sales=int(row.total_sales),
                order_count=int(row.order_count),
                average_order_value=avg_order_val
            ))
            if row.total_sales > peak_sales_amount:
                peak_sales_amount = int(row.total_sales)
                peak_sales_day = str(row.period)

        # Growth Percentage (compare with previous period of same length)
        # Calculate previous period
        duration = end_date - start_date
        prev_start_date = start_date - (duration + timedelta(days=1))
        prev_end_date = start_date - timedelta(days=1)

        prev_period_sales_query = db.query(OrderModel).filter(
            and_(
                OrderModel.ordered_at >= prev_start_date,
                OrderModel.ordered_at <= prev_end_date + timedelta(days=1),
                OrderModel.status == OrderStatus.COMPLETED
            )
        )
        if coffee_shop_id:
            prev_period_sales_query = prev_period_sales_query.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                            .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                            .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)
        
        total_revenue_prev_period = prev_period_sales_query.with_entities(func.sum(OrderModel.total_price)).scalar() or 0

        growth_percentage = 0.0
        if total_revenue_prev_period > 0:
            growth_percentage = ((total_revenue - total_revenue_prev_period) / total_revenue_prev_period) * 100
        elif total_revenue > 0:
            growth_percentage = 100.0

        return SalesAnalyticsResponse(
            total_revenue=total_revenue,
            total_orders=total_orders,
            average_order_value=average_order_value,
            growth_percentage=growth_percentage,
            sales_data=sales_data,
            peak_sales_day=peak_sales_day,
            peak_sales_amount=peak_sales_amount,
        )

    def get_revenue_analytics(
        self,
        db: Session,
        start_date: Optional[date],
        end_date: Optional[date],
        coffee_shop_id: Optional[UUID],
        group_by: str,
    ) -> RevenueAnalyticsResponse:
        """
        Mengambil analitik pendapatan.
        Catatan: Model Anda tidak secara eksplisit memiliki 'cost' atau 'profit_margin' per pesanan/item.
        Saya akan mengasumsikan profit margin 20% sebagai placeholder atau Anda dapat menghitungnya jika ada
        data biaya di database Anda.
        """
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        revenue_query_base = db.query(OrderModel).filter(
            and_(
                OrderModel.ordered_at >= start_date,
                OrderModel.ordered_at <= end_date + timedelta(days=1),
                OrderModel.status == OrderStatus.COMPLETED
            )
        )
        if coffee_shop_id:
            revenue_query_base = revenue_query_base.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                    .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                    .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)

        total_revenue = revenue_query_base.with_entities(func.sum(OrderModel.total_price)).scalar() or 0
        
        # Placeholder for profit calculation (assuming 20% profit margin)
        # Anda perlu mengganti ini jika Anda memiliki data biaya yang sebenarnya.
        total_profit = int(total_revenue * 0.20)
        average_profit_margin = 20.0 # Placeholder

        revenue_data: List[RevenueDataPoint] = []
        
        if group_by == "day":
            period_col = func.date(OrderModel.ordered_at).label("period")
        elif group_by == "week":
            period_col = func.to_char(OrderModel.ordered_at, 'YYYY-WW').label("period")
        elif group_by == "month":
            period_col = func.to_char(OrderModel.ordered_at, 'YYYY-MM').label("period")
        else:
            raise ValueError("Invalid group_by parameter.")

        revenue_data_query = revenue_query_base.with_entities(
            period_col,
            func.sum(OrderModel.total_price).label("revenue")
        ).group_by(period_col).order_by(period_col).all()

        highest_revenue = 0
        lowest_revenue = float('inf')
        highest_revenue_period = "N/A"
        lowest_revenue_period = "N/A"

        for row in revenue_data_query:
            period_revenue = int(row.revenue)
            period_profit = int(period_revenue * 0.20) # Placeholder
            period_cost = period_revenue - period_profit # Placeholder
            
            revenue_data.append(RevenueDataPoint(
                period=str(row.period),
                revenue=period_revenue,
                profit_margin=20.0, # Placeholder
                cost=period_cost
            ))
            if period_revenue > highest_revenue:
                highest_revenue = period_revenue
                highest_revenue_period = str(row.period)
            if period_revenue < lowest_revenue:
                lowest_revenue = period_revenue
                lowest_revenue_period = str(row.period)
        
        if not revenue_data: # Handle case where no data is found
            lowest_revenue_period = "N/A"

        return RevenueAnalyticsResponse(
            total_revenue=total_revenue,
            total_profit=total_profit,
            average_profit_margin=average_profit_margin,
            revenue_data=revenue_data,
            highest_revenue_period=highest_revenue_period,
            lowest_revenue_period=lowest_revenue_period,
        )

    def get_order_analytics(
        self,
        db: Session,
        start_date: Optional[date],
        end_date: Optional[date],
        coffee_shop_id: Optional[UUID],
    ) -> OrderAnalyticsResponse:
        """
        Mengambil analitik pesanan.
        """
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        orders_query_base = db.query(OrderModel).filter(
            and_(
                OrderModel.ordered_at >= start_date,
                OrderModel.ordered_at <= end_date + timedelta(days=1)
            )
        )
        if coffee_shop_id:
            orders_query_base = orders_query_base.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                    .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                    .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)

        total_orders = orders_query_base.count()
        completed_orders = orders_query_base.filter(OrderModel.status == OrderStatus.COMPLETED).count()
        cancelled_orders = orders_query_base.filter(OrderModel.status == OrderStatus.CANCELLED).count()
        pending_orders = orders_query_base.filter(OrderModel.status == OrderStatus.PENDING).count()
        
        completion_rate = (completed_orders / total_orders) * 100 if total_orders else 0.0
        cancellation_rate = (cancelled_orders / total_orders) * 100 if total_orders else 0.0

        # Average Preparation Time (Requires logic to track status changes or a 'preparation_time' field)
        # For now, a placeholder or if you have 'created_at' to 'completed' time tracking.
        # This is a rough estimation assuming 'ordered_at' to 'updated_at' (if 'updated_at' is set to completion time)
        avg_prep_time_query = db.query(
            func.avg(extract('epoch', OrderModel.updated_at - OrderModel.ordered_at)) # Seconds difference
        ).filter(
            and_(
                OrderModel.ordered_at >= start_date,
                OrderModel.ordered_at <= end_date + timedelta(days=1),
                OrderModel.status == OrderStatus.COMPLETED
            )
        )
        if coffee_shop_id:
            avg_prep_time_query = avg_prep_time_query.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                    .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                    .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)
        
        avg_prep_time_seconds = avg_prep_time_query.scalar() or 0
        average_preparation_time = round(avg_prep_time_seconds / 60, 2) # Convert to minutes

        # Peak Order Hour
        peak_order_hour_query = orders_query_base.with_entities(
            extract('hour', OrderModel.ordered_at).label('hour'),
            func.count(OrderModel.id).label('order_count')
        ).group_by('hour').order_by(func.count(OrderModel.id).desc()).limit(1).first()

        peak_order_hour = int(peak_order_hour_query.hour) if peak_order_hour_query else 0

        # Order Status Distribution
        order_status_distribution_query = orders_query_base.with_entities(
            OrderModel.status,
            func.count(OrderModel.id)
        ).group_by(OrderModel.status).all()

        order_status_distribution = {status.value: count for status, count in order_status_distribution_query}

        return OrderAnalyticsResponse(
            total_orders=total_orders,
            completed_orders=completed_orders,
            cancelled_orders=cancelled_orders,
            pending_orders=pending_orders,
            completion_rate=completion_rate,
            cancellation_rate=cancellation_rate,
            average_preparation_time=average_preparation_time,
            peak_order_hour=peak_order_hour,
            order_status_distribution=order_status_distribution,
        )

    def get_user_analytics(
        self,
        db: Session,
        start_date: Optional[date],
        end_date: Optional[date],
        coffee_shop_id: Optional[UUID], # This filter will be applied to user's orders
    ) -> UserAnalyticsResponse:
        """
        Mengambil analitik pengguna.
        """
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        # Total Users (all users in the system)
        total_users = db.query(UserModel).filter(UserModel.role_id == db.query(RoleModel.id).filter(RoleModel.role == Role.USER).scalar()).count()

        # New Users This Period
        new_users_this_period = db.query(UserModel).filter(
            and_(
                UserModel.created_at >= start_date,
                UserModel.created_at <= end_date + timedelta(days=1),
                UserModel.role_id == db.query(RoleModel.id).filter(RoleModel.role == Role.USER).scalar()
            )
        ).count()

        # Active Users (users with at least one completed order in the period)
        active_users_query = db.query(distinct(OrderModel.user_id)).filter(
            and_(
                OrderModel.ordered_at >= start_date,
                OrderModel.ordered_at <= end_date + timedelta(days=1),
                OrderModel.status == OrderStatus.COMPLETED
            )
        )
        if coffee_shop_id:
            active_users_query = active_users_query.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                    .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                    .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)
        active_users = active_users_query.count()

        # Returning Customers & Retention Rate
        # A returning customer is a user who made an order in the previous period AND this period.
        # This requires defining a "previous period" and querying for users in both.
        # For simplicity, here, a returning customer is one with > 1 order in the system, or within the period.
        # Let's refine: users who ordered in this period and also ordered BEFORE this period.
        
        # Users who ordered in the current period
        users_in_current_period = db.query(distinct(OrderModel.user_id)).filter(
            and_(
                OrderModel.ordered_at >= start_date,
                OrderModel.ordered_at <= end_date + timedelta(days=1),
                OrderModel.status == OrderStatus.COMPLETED
            )
        )
        if coffee_shop_id:
            users_in_current_period = users_in_current_period.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                            .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                            .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)
        users_in_current_period_ids = [u_id for u_id, in users_in_current_period.all()]

        # Users who ordered before the current period AND are in the current period
        returning_customers_query = db.query(distinct(OrderModel.user_id)).filter(
            and_(
                OrderModel.ordered_at < start_date,
                OrderModel.status == OrderStatus.COMPLETED,
                OrderModel.user_id.in_(users_in_current_period_ids)
            )
        )
        if coffee_shop_id:
            returning_customers_query = returning_customers_query.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                                .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                                .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)
        returning_customers = returning_customers_query.count()

        customer_retention_rate = (returning_customers / len(users_in_current_period_ids)) * 100 if users_in_current_period_ids else 0.0

        # Average Orders Per User (for active users in the period)
        avg_orders_per_user_query = db.query(
            func.count(OrderModel.id) / func.count(distinct(OrderModel.user_id))
        ).filter(
            and_(
                OrderModel.ordered_at >= start_date,
                OrderModel.ordered_at <= end_date + timedelta(days=1),
                OrderModel.status == OrderStatus.COMPLETED
            )
        )
        if coffee_shop_id:
            avg_orders_per_user_query = avg_orders_per_user_query.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                                .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                                .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)
        average_orders_per_user = round(avg_orders_per_user_query.scalar() or 0.0, 2)

        # Top Customers (by total spent or total orders)
        top_customers_query = db.query(
            UserModel.name,
            UserModel.email,
            func.count(OrderModel.id).label("total_orders"),
            func.sum(OrderModel.total_price).label("total_spent")
        ).join(OrderModel, UserModel.id == OrderModel.user_id).filter(
            and_(
                OrderModel.ordered_at >= start_date,
                OrderModel.ordered_at <= end_date + timedelta(days=1),
                OrderModel.status == OrderStatus.COMPLETED
            )
        )
        if coffee_shop_id:
            top_customers_query = top_customers_query.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                    .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                    .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)
        
        top_customers = top_customers_query.group_by(UserModel.name, UserModel.email)\
                                            .order_by(func.sum(OrderModel.total_price).desc())\
                                            .limit(10).all()
        
        top_customers_formatted = [
            {"name": tc.name, "email": tc.email, "total_orders": tc.total_orders, "total_spent": int(tc.total_spent)}
            for tc in top_customers
        ]

        return UserAnalyticsResponse(
            total_users=total_users,
            new_users_this_period=new_users_this_period,
            active_users=active_users,
            returning_customers=returning_customers,
            customer_retention_rate=customer_retention_rate,
            average_orders_per_user=average_orders_per_user,
            top_customers=top_customers_formatted,
        )

    def get_coffee_shop_analytics(
        self, db: Session, start_date: Optional[date], end_date: Optional[date]
    ) -> CoffeeShopAnalyticsResponse:
        """
        Mengambil analitik performa kedai kopi.
        """
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        total_coffee_shops = db.query(CoffeeShopModel).count()

        # Top Performing Shops
        shop_performance_query = db.query(
            CoffeeShopModel.id.label("coffee_shop_id"),
            CoffeeShopModel.name.label("coffee_shop_name"),
            func.sum(OrderModel.total_price).label("total_revenue"),
            func.count(OrderModel.id).label("total_orders"),
            func.avg(RatingModel.rating).label("avg_customer_satisfaction") # Assuming RatingModel links to CoffeeMenuModel
        ).outerjoin(
            CoffeeMenuModel, CoffeeShopModel.id == CoffeeMenuModel.coffee_shop_id
        ).outerjoin(
            OrderItemModel, CoffeeMenuModel.id == OrderItemModel.coffee_id
        ).outerjoin(
            OrderModel, OrderItemModel.order_id == OrderModel.id
        ).outerjoin( # Join RatingModel to CoffeeMenuModel to get satisfaction
            RatingModel, CoffeeMenuModel.id == RatingModel.coffee_id
        ).filter(
            and_(
                OrderModel.ordered_at >= start_date,
                OrderModel.ordered_at <= end_date + timedelta(days=1),
                OrderModel.status == OrderStatus.COMPLETED
            ) if OrderModel.id is not None else True # Apply filter only if orders exist
        ).group_by(CoffeeShopModel.id, CoffeeShopModel.name)\
        .order_by(func.sum(OrderModel.total_price).desc().nulls_last()) # Handle shops with no orders
        
        all_shop_performance = shop_performance_query.all()

        top_performing_shops: List[CoffeeShopPerformance] = []
        rank = 1
        for row in all_shop_performance:
            total_revenue = int(row.total_revenue) if row.total_revenue else 0
            total_orders = int(row.total_orders) if row.total_orders else 0
            avg_order_value = int(total_revenue / total_orders) if total_orders else 0
            customer_satisfaction = round(float(row.avg_customer_satisfaction), 2) if row.avg_customer_satisfaction else None

            top_performing_shops.append(CoffeeShopPerformance(
                coffee_shop_id=str(row.coffee_shop_id),
                coffee_shop_name=row.coffee_shop_name,
                total_revenue=total_revenue,
                total_orders=total_orders,
                average_order_value=avg_order_value,
                customer_satisfaction=customer_satisfaction,
                performance_rank=rank
            ))
            rank += 1

        # Total Revenue All Shops
        total_revenue_all_shops = db.query(func.sum(OrderModel.total_price))\
                                    .filter(
                                        and_(
                                            OrderModel.ordered_at >= start_date,
                                            OrderModel.ordered_at <= end_date + timedelta(days=1),
                                            OrderModel.status == OrderStatus.COMPLETED
                                        )
                                    ).scalar() or 0

        average_revenue_per_shop = int(total_revenue_all_shops / total_coffee_shops) if total_coffee_shops else 0

        return CoffeeShopAnalyticsResponse(
            total_coffee_shops=total_coffee_shops,
            top_performing_shops=top_performing_shops,
            total_revenue_all_shops=total_revenue_all_shops,
            average_revenue_per_shop=average_revenue_per_shop,
        )

    def get_popular_items(
        self,
        db: Session,
        start_date: Optional[date],
        end_date: Optional[date],
        coffee_shop_id: Optional[UUID],
        limit: int,
    ) -> PopularItemsResponse:
        """
        Mengambil analitik item menu populer.
        """
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        popular_items_query = db.query(
            CoffeeMenuModel.id.label("coffee_id"),
            CoffeeMenuModel.name.label("coffee_name"),
            func.sum(OrderItemModel.quantity).label("total_quantity"),
            func.sum(OrderItemModel.subtotal).label("total_revenue"), # Assuming subtotal is price * quantity for that item
            func.count(distinct(OrderModel.id)).label("order_frequency") # Count unique orders containing this item
        ).join(OrderItemModel, CoffeeMenuModel.id == OrderItemModel.coffee_id)\
        .join(OrderModel, OrderItemModel.order_id == OrderModel.id)\
        .filter(
            and_(
                OrderModel.ordered_at >= start_date,
                OrderModel.ordered_at <= end_date + timedelta(days=1),
                OrderModel.status == OrderStatus.COMPLETED
            )
        )
        if coffee_shop_id:
            popular_items_query = popular_items_query.filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)
        
        popular_items_data = popular_items_query.group_by(CoffeeMenuModel.id, CoffeeMenuModel.name)\
                                                .order_by(func.sum(OrderItemModel.quantity).desc())\
                                                .limit(limit).all()

        popular_items: List[PopularItem] = []
        rank = 1
        for row in popular_items_data:
            popular_items.append(PopularItem(
                coffee_id=str(row.coffee_id),
                coffee_name=row.coffee_name,
                total_quantity=int(row.total_quantity),
                total_revenue=int(row.total_revenue) if row.total_revenue else 0,
                order_frequency=int(row.order_frequency),
                rank=rank
            ))
            rank += 1

        total_items_analyzed = db.query(CoffeeMenuModel).count() # Or count of unique items sold in period
        analysis_period = f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"

        return PopularItemsResponse(
            popular_items=popular_items,
            total_items_analyzed=total_items_analyzed,
            analysis_period=analysis_period,
        )

    def get_customer_behavior_analytics(
        self,
        db: Session,
        start_date: Optional[date],
        end_date: Optional[date],
        coffee_shop_id: Optional[UUID],
    ) -> CustomerBehaviorResponse:
        """
        Mengambil analitik perilaku pelanggan.
        """
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        customer_segments: List[CustomerSegment] = []
        
        # Peak Ordering Hours
        peak_ordering_hours_query = db.query(
            extract('hour', OrderModel.ordered_at).label('hour'),
            func.count(OrderModel.id).label('order_count')
        ).filter(
            and_(
                OrderModel.ordered_at >= start_date,
                OrderModel.ordered_at <= end_date + timedelta(days=1),
                OrderModel.status == OrderStatus.COMPLETED
            )
        )
        if coffee_shop_id:
            peak_ordering_hours_query = peak_ordering_hours_query.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                                    .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                                    .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)
        
        peak_ordering_hours_result = peak_ordering_hours_query.group_by('hour').order_by(func.count(OrderModel.id).desc()).all()
        
        # Get hours with highest order counts. If multiple hours have the same max count, include all.
        peak_order_counts = [row.order_count for row in peak_ordering_hours_result]
        if peak_order_counts:
            max_order_count = max(peak_order_counts)
            peak_ordering_hours = [int(row.hour) for row in peak_ordering_hours_result if row.order_count == max_order_count]
        else:
            peak_ordering_hours = []


        average_session_duration = 0.0 # This needs client-side tracking or more complex inference
        
        # Repeat Customer Rate (Users who ordered more than once in the period)
        repeat_customer_query = db.query(
            OrderModel.user_id,
            func.count(OrderModel.id).label('order_count')
        ).filter(
            and_(
                OrderModel.ordered_at >= start_date,
                OrderModel.ordered_at <= end_date + timedelta(days=1),
                OrderModel.status == OrderStatus.COMPLETED
            )
        )
        if coffee_shop_id:
            repeat_customer_query = repeat_customer_query.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                        .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                        .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)

        repeat_customer_counts = repeat_customer_query.group_by(OrderModel.user_id).having(func.count(OrderModel.id) > 1).count()
        
        total_unique_customers_in_period = db.query(distinct(OrderModel.user_id)).filter(
            and_(
                OrderModel.ordered_at >= start_date,
                OrderModel.ordered_at <= end_date + timedelta(days=1),
                OrderModel.status == OrderStatus.COMPLETED
            )
        )
        if coffee_shop_id:
            total_unique_customers_in_period = total_unique_customers_in_period.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                                                .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                                                .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)
        total_unique_customers_in_period = total_unique_customers_in_period.count()

        repeat_customer_rate = (repeat_customer_counts / total_unique_customers_in_period) * 100 if total_unique_customers_in_period else 0.0

        # New vs Returning Ratio (Based on new_users_this_period and returning_customers from get_user_analytics)
        user_analytics = self.get_user_analytics(db, start_date, end_date, coffee_shop_id)
        new_users = user_analytics.new_users_this_period
        returning_users = user_analytics.returning_customers # Reusing definition from user analytics
        
        new_vs_returning_ratio: Dict[str, float] = {}
        if (new_users + returning_users) > 0:
            new_vs_returning_ratio["new"] = new_users / (new_users + returning_users)
            new_vs_returning_ratio["returning"] = returning_users / (new_users + returning_users)
        else:
            new_vs_returning_ratio = {"new": 0.0, "returning": 0.0}

        # Popular Payment Methods (assuming TransactionModel has a 'payment_method' or similar field)
        # Your TransactionModel only has status. If you add 'payment_method' field, you can use this.
        popular_payment_methods: Dict[str, int] = {}
        # Example if you had `TransactionModel.payment_method`:
        # payment_method_query = db.query(
        #     TransactionModel.payment_method,
        #     func.count(TransactionModel.id)
        # ).join(OrderModel, TransactionModel.order_id == OrderModel.id).filter(
        #     and_(
        #         TransactionModel.payment_time >= start_date,
        #         TransactionModel.payment_time <= end_date + timedelta(days=1),
        #         TransactionModel.status == StatusType.SUCCESS
        #     )
        # )
        # if coffee_shop_id:
        #     payment_method_query = payment_method_query.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
        #                                                 .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
        #                                                 .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)
        # popular_payment_methods_result = payment_method_query.group_by(TransactionModel.payment_method).all()
        # popular_payment_methods = {method: count for method, count in popular_payment_methods_result}

        # Customer Segments (Placeholder for now, requires more complex logic like RFM)
        # For a basic example, we can segment by total spent.
        customer_spending_query = db.query(
            UserModel.id,
            func.sum(OrderModel.total_price).label("total_spent"),
            func.count(OrderModel.id).label("total_orders")
        ).join(OrderModel, UserModel.id == OrderModel.user_id).filter(
            and_(
                OrderModel.ordered_at >= start_date,
                OrderModel.ordered_at <= end_date + timedelta(days=1),
                OrderModel.status == OrderStatus.COMPLETED
            )
        )
        if coffee_shop_id:
            customer_spending_query = customer_spending_query.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                            .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                            .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)

        customer_spending_data = customer_spending_query.group_by(UserModel.id).all()
        
        total_spent_all_customers = sum(s.total_spent for s in customer_spending_data if s.total_spent)
        
        # Simple segmentation: High Value (top 20%), Medium Value (next 30%), Low Value (rest)
        sorted_customers = sorted(customer_spending_data, key=lambda x: x.total_spent if x.total_spent else 0, reverse=True)
        
        num_customers = len(sorted_customers)
        high_value_count = int(num_customers * 0.20)
        medium_value_count = int(num_customers * 0.30)
        
        segment_high_value = sorted_customers[:high_value_count]
        segment_medium_value = sorted_customers[high_value_count : high_value_count + medium_value_count]
        segment_low_value = sorted_customers[high_value_count + medium_value_count:]

        def calculate_segment_metrics(segment_list, name):
            count = len(segment_list)
            avg_aov = sum(s.total_spent for s in segment_list if s.total_spent) / sum(s.total_orders for s in segment_list) if sum(s.total_orders for s in segment_list) else 0
            total_rev = sum(s.total_spent for s in segment_list if s.total_spent)
            percentage = (total_rev / total_spent_all_customers) * 100 if total_spent_all_customers else 0
            return CustomerSegment(
                segment_name=name,
                customer_count=count,
                average_order_value=int(avg_aov),
                total_revenue=int(total_rev),
                percentage_of_total=round(percentage, 2)
            )

        if segment_high_value:
            customer_segments.append(calculate_segment_metrics(segment_high_value, "High Value Customers"))
        if segment_medium_value:
            customer_segments.append(calculate_segment_metrics(segment_medium_value, "Medium Value Customers"))
        if segment_low_value:
            customer_segments.append(calculate_segment_metrics(segment_low_value, "Low Value Customers"))
        

        return CustomerBehaviorResponse(
            customer_segments=customer_segments,
            peak_ordering_hours=peak_ordering_hours,
            average_session_duration=average_session_duration,
            repeat_customer_rate=repeat_customer_rate,
            new_vs_returning_ratio=new_vs_returning_ratio,
            popular_payment_methods=popular_payment_methods,
        )

    def get_date_range_analytics(
        self,
        db: Session,
        start_date: date,
        end_date: date,
        coffee_shop_id: Optional[UUID],
    ) -> DateRangeAnalytics:
        """
        Mengambil analitik komprehensif untuk rentang tanggal tertentu.
        """
        # Reuse existing service methods or combine queries for efficiency

        # Total Revenue, Total Orders, Average Order Value
        sales_analytics = self.get_sales_analytics(db, start_date, end_date, coffee_shop_id, "day")
        total_revenue = sales_analytics.total_revenue
        total_orders = sales_analytics.total_orders
        average_order_value = sales_analytics.average_order_value
        daily_revenue = sales_analytics.sales_data

        # Total Bookings
        bookings_query_base = db.query(BookingModel).filter(
            and_(
                BookingModel.booking_date >= start_date,
                BookingModel.booking_date <= end_date + timedelta(days=1),
                BookingModel.status == BookingStatus.SUCCESS
            )
        )
        if coffee_shop_id:
            bookings_query_base = bookings_query_base.join(BookingTableModel, BookingModel.id == BookingTableModel.booking_id)\
                                                    .join(TableModel, BookingTableModel.table_id == TableModel.id)\
                                                    .filter(TableModel.coffee_shop_id == coffee_shop_id)
        total_bookings = bookings_query_base.count()

        # Unique Customers (users who placed at least one order)
        unique_customers_query = db.query(distinct(OrderModel.user_id)).filter(
            and_(
                OrderModel.ordered_at >= start_date,
                OrderModel.ordered_at <= end_date + timedelta(days=1),
                OrderModel.status == OrderStatus.COMPLETED
            )
        )
        if coffee_shop_id:
            unique_customers_query = unique_customers_query.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                            .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                            .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)
        unique_customers = unique_customers_query.count()

        # Customer Acquisition Cost (requires tracking marketing spend / new users) - Placeholder
        customer_acquisition_cost = 0.0

        # Customer Lifetime Value (requires historical revenue per customer) - Placeholder
        customer_lifetime_value = 0.0

        # Trends (simplified: compare with previous period)
        duration = end_date - start_date
        prev_start_date = start_date - (duration + timedelta(days=1))
        prev_end_date = start_date - timedelta(days=1)

        prev_period_sales_analytics = self.get_sales_analytics(db, prev_start_date, prev_end_date, coffee_shop_id, "day")
        
        revenue_trend = "stable"
        if total_revenue > prev_period_sales_analytics.total_revenue:
            revenue_trend = "increasing"
        elif total_revenue < prev_period_sales_analytics.total_revenue:
            revenue_trend = "decreasing"

        order_trend = "stable"
        if total_orders > prev_period_sales_analytics.total_orders:
            order_trend = "increasing"
        elif total_orders < prev_period_sales_analytics.total_orders:
            order_trend = "decreasing"

        prev_period_unique_customers_query = db.query(distinct(OrderModel.user_id)).filter(
            and_(
                OrderModel.ordered_at >= prev_start_date,
                OrderModel.ordered_at <= prev_end_date + timedelta(days=1),
                OrderModel.status == OrderStatus.COMPLETED
            )
        )
        if coffee_shop_id:
            prev_period_unique_customers_query = prev_period_unique_customers_query.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                                                    .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                                                    .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)
        prev_period_unique_customers = prev_period_unique_customers_query.count()

        customer_trend = "stable"
        if unique_customers > prev_period_unique_customers:
            customer_trend = "increasing"
        elif unique_customers < prev_period_unique_customers:
            customer_trend = "decreasing"

        # Comparisons (percentage changes)
        previous_period_comparison: Dict[str, float] = {
            "revenue_change": sales_analytics.growth_percentage,
            "order_change": ((total_orders - prev_period_sales_analytics.total_orders) / prev_period_sales_analytics.total_orders) * 100 if prev_period_sales_analytics.total_orders else (100.0 if total_orders > 0 else 0.0),
            "customer_change": ((unique_customers - prev_period_unique_customers) / prev_period_unique_customers) * 100 if prev_period_unique_customers else (100.0 if unique_customers > 0 else 0.0),
        }

        # Top performers
        top_selling_items = self.get_popular_items(db, start_date, end_date, coffee_shop_id, 5).popular_items
        top_customers = self.get_user_analytics(db, start_date, end_date, coffee_shop_id).top_customers
        
        best_performing_days_query = db.query(
            func.date(OrderModel.ordered_at).label("order_date"),
            func.sum(OrderModel.total_price).label("daily_revenue")
        ).filter(
            and_(
                OrderModel.ordered_at >= start_date,
                OrderModel.ordered_at <= end_date + timedelta(days=1),
                OrderModel.status == OrderStatus.COMPLETED
            )
        )
        if coffee_shop_id:
            best_performing_days_query = best_performing_days_query.join(OrderItemModel, OrderModel.id == OrderItemModel.order_id)\
                                                                    .join(CoffeeMenuModel, OrderItemModel.coffee_id == CoffeeMenuModel.id)\
                                                                    .filter(CoffeeMenuModel.coffee_shop_id == coffee_shop_id)

        best_performing_days_result = best_performing_days_query.group_by("order_date")\
                                                                .order_by(func.sum(OrderModel.total_price).desc())\
                                                                .limit(3).all() # Top 3 days

        best_performing_days = [str(row.order_date) for row in best_performing_days_result]


        return DateRangeAnalytics(
            period_start=start_date,
            period_end=end_date,
            total_revenue=total_revenue,
            total_orders=total_orders,
            total_bookings=total_bookings,
            unique_customers=unique_customers,
            daily_revenue=daily_revenue,
            average_order_value=average_order_value,
            customer_acquisition_cost=customer_acquisition_cost,
            customer_lifetime_value=customer_lifetime_value,
            revenue_trend=revenue_trend,
            order_trend=order_trend,
            customer_trend=customer_trend,
            previous_period_comparison=previous_period_comparison,
            top_selling_items=top_selling_items,
            top_customers=top_customers,
            best_performing_days=best_performing_days,
        )

    def export_analytics_csv(
        self,
        db: Session,
        report_type: str,
        start_date: Optional[date],
        end_date: Optional[date],
        coffee_shop_id: Optional[UUID],
    ):
        """
        Mengekspor data analitik sebagai CSV.
        """
        from fastapi.responses import StreamingResponse
        import io
        import csv

        output = io.StringIO()
        writer = csv.writer(output)

        headers: List[str] = []
        data_rows: List[List[Any]] = []

        if report_type == "sales":
            analytics_data = self.get_sales_analytics(db, start_date, end_date, coffee_shop_id, "day")
            headers = ["Date", "Total Sales", "Order Count", "Average Order Value"]
            for dp in analytics_data.sales_data:
                data_rows.append([dp.date, dp.total_sales, dp.order_count, dp.average_order_value])
        elif report_type == "orders":
            analytics_data = self.get_order_analytics(db, start_date, end_date, coffee_shop_id)
            headers = ["Total Orders", "Completed Orders", "Cancelled Orders", "Pending Orders", "Completion Rate (%)", "Cancellation Rate (%)", "Avg Prep Time (minutes)", "Peak Order Hour"]
            data_rows.append([
                analytics_data.total_orders,
                analytics_data.completed_orders,
                analytics_data.cancelled_orders,
                analytics_data.pending_orders,
                round(analytics_data.completion_rate, 2),
                round(analytics_data.cancellation_rate, 2),
                round(analytics_data.average_preparation_time, 2),
                analytics_data.peak_order_hour
            ])
            # Add order status distribution separately if desired
            for status, count in analytics_data.order_status_distribution.items():
                data_rows.append([f"Status: {status}", count, "", ""])
        elif report_type == "users":
            analytics_data = self.get_user_analytics(db, start_date, end_date, coffee_shop_id)
            headers = ["Metric", "Value"]
            data_rows.append(["Total Users", analytics_data.total_users])
            data_rows.append(["New Users This Period", analytics_data.new_users_this_period])
            data_rows.append(["Active Users", analytics_data.active_users])
            data_rows.append(["Returning Customers", analytics_data.returning_customers])
            data_rows.append(["Customer Retention Rate (%)", round(analytics_data.customer_retention_rate, 2)])
            data_rows.append(["Average Orders Per User", round(analytics_data.average_orders_per_user, 2)])
            
            writer.writerow(headers)
            writer.writerows(data_rows)

            if analytics_data.top_customers:
                writer.writerow([]) # Blank row for separation
                writer.writerow(["Top Customers"])
                writer.writerow(["Name", "Email", "Total Orders", "Total Spent"])
                for customer in analytics_data.top_customers:
                    writer.writerow([customer["name"], customer["email"], customer["total_orders"], customer["total_spent"]])
                
                output.seek(0)
                return StreamingResponse(
                    output,
                    media_type="text/csv",
                    headers={"Content-Disposition": f"attachment; filename=analytics_{report_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"}
                )

        elif report_type == "revenue":
            analytics_data = self.get_revenue_analytics(db, start_date, end_date, coffee_shop_id, "day")
            headers = ["Period", "Revenue", "Profit Margin (%)", "Cost"]
            for dp in analytics_data.revenue_data:
                data_rows.append([dp.period, dp.revenue, round(dp.profit_margin, 2), dp.cost])
        else:
            raise ValueError("Invalid report type")

        writer.writerow(headers)
        writer.writerows(data_rows)
        
        output.seek(0)
        return StreamingResponse(
            output,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=analytics_{report_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"}
        )


admin_analytics_service = AdminAnalyticsService()