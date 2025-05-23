"""
Models package initializer
Import all models to make them available when importing the models package
"""
from app.models.base import BaseModel
from app.models.user import Role, RoleModel, UserModel
from app.models.coffee import (
    CoffeeShopModel, 
    CoffeeMenuModel, 
    VariantTypeModel, 
    VariantModel, 
    CoffeeVariantModel,
)
from app.models.order import (
    OrderStatus, 
    StatusType, 
    OrderModel, 
    OrderItemModel,
    OrderItemVariantModel, 
    TransactionModel, 
    PayoutModel,
)
from app.models.booking import (
    BookingStatus, 
    TableModel, 
    BookingModel, 
    BookingTableModel,
)
from app.models.notification import (
    NotificationModel, 
    UserFavoriteModel, 
    RatingModel,
)
from app.models.booking_status_history import BookingStatusHistoryModel
from app.models.order_status_history import OrderStatusHistoryModel
from app.models.operating_hours import (
    WeekDay,
    TimeSlotModel,
    OperatingHoursModel
)

# List of all models for easy access
__all__ = [
    "BaseModel",
    "Role",
    "RoleModel",
    "UserModel",
    "CoffeeShopModel",
    "CoffeeMenuModel",
    "VariantTypeModel",
    "VariantModel",
    "CoffeeVariantModel",
    "OrderStatus",
    "StatusType",
    "OrderModel",
    "OrderItemModel",
    "OrderItemVariantModel",
    "TransactionModel",
    "PayoutModel",
    "BookingStatus",
    "TableModel",
    "BookingModel",
    "BookingTableModel",
    "NotificationModel",
    "UserFavoriteModel",
    "RatingModel",
    "BookingStatusHistoryModel",
    "OrderStatusHistoryModel",
    "WeekDay",
    "TimeSlotModel",
    "OperatingHoursModel"
]
