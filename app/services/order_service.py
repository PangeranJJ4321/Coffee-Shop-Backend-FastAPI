"""
Order service for managing coffee orders
"""
import uuid
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, desc

from app.models.order import (
    OrderModel, 
    OrderStatus, 
    OrderItemModel, 
    OrderItemVariantModel
)
from app.models.coffee import CoffeeMenuModel, VariantModel
from app.schemas.order_schema import OrderCreate, OrderFilterParams


class OrderService:
    def create_order(self, db: Session, order_data: OrderCreate, user_id: uuid.UUID):
        """Create a new order with order items and variants"""
        # Calculate total price
        total_price = 0
        order_items_data = []
        
        # Process each order item
        for item in order_data.order_items:
            # Get coffee price
            coffee = db.query(CoffeeMenuModel).filter_by(id=item.coffee_id).first()
            if not coffee or not coffee.is_available:
                raise ValueError(f"Coffee with ID {item.coffee_id} not available")
            
            item_price = coffee.price
            
            # Get variant prices
            variants_data = []
            for variant_data in item.variants:
                variant = db.query(VariantModel).filter_by(id=variant_data.variant_id).first()
                if not variant or not variant.is_available:
                    raise ValueError(f"Variant with ID {variant_data.variant_id} not available")
                item_price += variant.additional_price
                variants_data.append(variant_data)
            
            # Calculate subtotal for this item
            subtotal = item_price * item.quantity
            total_price += subtotal
            
            order_items_data.append({
                "coffee_id": item.coffee_id,
                "quantity": item.quantity,
                "subtotal": subtotal,
                "variants": variants_data
            })
        
        # Create order
        order = OrderModel(
            order_id=f"ORD-{uuid.uuid4().hex[:8].upper()}",
            user_id=user_id,
            total_price=total_price,
            status=OrderStatus.PENDING,
            ordered_at=datetime.utcnow(),
            booking_id=order_data.booking_id
        )
        db.add(order)
        db.flush()
        
        # Create order items
        for item_data in order_items_data:
            order_item = OrderItemModel(
                order_id=order.id,
                coffee_id=item_data["coffee_id"],
                quantity=item_data["quantity"],
                subtotal=item_data["subtotal"]
            )
            db.add(order_item)
            db.flush()
            
            # Create order item variants
            for variant_data in item_data["variants"]:
                order_item_variant = OrderItemVariantModel(
                    order_item_id=order_item.id,
                    variant_id=variant_data.variant_id
                )
                db.add(order_item_variant)
        
        db.commit()
        db.refresh(order)
        return order

    def get_user_orders(self, db: Session, user_id: uuid.UUID, params: OrderFilterParams):
        """Get all orders for a user with optional filtering"""
        query = db.query(OrderModel).filter(OrderModel.user_id == user_id)
        
        # Apply filters
        if params.status:
            try:
                status_enum = OrderStatus[params.status.upper()]
                query = query.filter(OrderModel.status == status_enum)
            except KeyError:
                # Invalid status, ignore filter
                pass
        
        if params.start_date:
            query = query.filter(OrderModel.ordered_at >= params.start_date)
        
        if params.end_date:
            query = query.filter(OrderModel.ordered_at <= params.end_date)
        
        # Sort by most recent first
        query = query.order_by(desc(OrderModel.ordered_at))
        
        # Apply pagination
        query = query.limit(params.limit).offset(params.offset)
        
        return query.all()

    def get_order_by_id(self, db: Session, order_id: uuid.UUID, user_id: uuid.UUID):
        """Get a single order with its items and variants"""
        order = db.query(OrderModel).filter(
            OrderModel.id == order_id,
            OrderModel.user_id == user_id
        ).options(
            joinedload(OrderModel.order_items).joinedload(OrderItemModel.variants).joinedload(OrderItemVariantModel.variant)
        ).first()
        
        if not order:
            return None
        
        # Enrich order items with coffee name and variants with names
        for item in order.order_items:
            coffee = db.query(CoffeeMenuModel).filter(CoffeeMenuModel.id == item.coffee_id).first()
            item.coffee_name = coffee.name if coffee else "Unknown Coffee"
            
            for variant_item in item.variants:
                variant = variant_item.variant
                variant_item.name = variant.name
                variant_item.variant_type = db.query(VariantTypeModel).filter(
                    VariantTypeModel.id == variant.variant_type_id
                ).first().name
                variant_item.additional_price = variant.additional_price
        
        return order

    def cancel_order(self, db: Session, order_id: uuid.UUID, user_id: uuid.UUID):
        """Cancel an order if it's in PENDING state"""
        order = db.query(OrderModel).filter(
            OrderModel.id == order_id,
            OrderModel.user_id == user_id,
            OrderModel.status == OrderStatus.PENDING
        ).first()
        
        if not order:
            return False
        
        order.status = OrderStatus.CANCELLED
        db.commit()
        return True


# Import after class definition to avoid circular imports
from app.models.coffee import VariantTypeModel

# Create singleton instance
order_service = OrderService()