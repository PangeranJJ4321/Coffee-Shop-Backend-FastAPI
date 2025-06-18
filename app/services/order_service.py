# app/services/order_service.py - DIREVISI
import uuid
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, and_, desc, func

from app.models.booking import BookingModel
from app.models.order import (
    OrderModel, 
    OrderStatus, 
    OrderItemModel, 
    OrderItemVariantModel
)
from app.models.coffee import CoffeeMenuModel, CoffeeVariantModel, VariantModel, VariantTypeModel, CoffeeShopModel
from app.models.user import UserModel
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
                
                # Cek apakah varian ini terhubung dengan kopi
                # Ini penting untuk mencegah user memilih varian yang tidak valid untuk kopi tsb
                coffee_variant = db.query(CoffeeMenuModel).join(CoffeeMenuModel.coffee_variants)\
                                .filter(CoffeeMenuModel.id == coffee.id, CoffeeVariantModel.variant_id == variant.id).first()
                if not coffee_variant:
                    raise ValueError(f"Variant {variant.name} is not available for coffee {coffee.name}")

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
            delivery_method=order_data.delivery_info.delivery_method,
            recipient_name=order_data.delivery_info.name, 
            recipient_phone_number=order_data.delivery_info.phone_number, 
            delivery_address=order_data.delivery_info.address if order_data.delivery_info.delivery_method == 'delivery' else None, # Tambahkan ini
            order_notes=order_data.delivery_info.notes 
            # booking_id=order_data.booking_id # Ini harusnya di set di tempat lain jika booking_id ada
        )
        db.add(order)
        db.flush() # Flush untuk mendapatkan order.id

        # Buat order items
        for item_data in order_items_data:
            order_item = OrderItemModel(
                order_id=order.id,
                coffee_id=item_data["coffee_id"],
                quantity=item_data["quantity"],
                subtotal=item_data["subtotal"]
            )
            db.add(order_item)
            db.flush() # Flush untuk mendapatkan order_item.id
            
            # Create order item variants
            for variant_data in item_data["variants"]:
                order_item_variant = OrderItemVariantModel(
                    order_item_id=order_item.id,
                    variant_id=variant_data.variant_id
                )
                db.add(order_item_variant)

        if order_data.booking_id:
            booking = db.query(BookingModel).filter(BookingModel.id == order_data.booking_id).first()
            if booking:
                booking.order_id = order.id
            else:
                pass
        
        db.commit()
        db.refresh(order)
        return order

    def get_user_orders(self, db: Session, user_id: uuid.UUID, params: OrderFilterParams):
        """Get all orders for a user with optional filtering"""
        query = db.query(OrderModel).filter(
            or_(
                OrderModel.user_id == user_id,  # Orders created by user
                OrderModel.paid_by_user_id == user_id  # Orders paid by user
            )
        ).options(
            joinedload(OrderModel.user),
            joinedload(OrderModel.paid_by_user),
            joinedload(OrderModel.order_items).joinedload(OrderItemModel.coffee),
            joinedload(OrderModel.order_items).joinedload(OrderItemModel.variants).joinedload(OrderItemVariantModel.variant).joinedload(VariantModel.variant_type)
        )
        
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
        
        orders = query.all()
        
        # Enrich with paid_by_user_name
        for order in orders:
            for item in order.order_items:
                # Ini diperlukan jika OrderItemResponse.coffee_name Anda tidak otomatis dipetakan dari item.coffee.name
                item.coffee_name = item.coffee.name # Menarik nama dari objek coffee yang dimuat

                # Tidak perlu mengatur item.coffee.image_url, item.coffee.description, item.coffee.price di sini,
                # karena `from_attributes = True` di CoffeeMenuResponseForOrderItem akan mengambilnya langsung
                # dari objek `item.coffee` (yang adalah `CoffeeMenuModel`) yang sudah di-load.

                for variant_item in item.variants:
                    variant = variant_item.variant
                    variant_item.name = variant.name
                    variant_item.variant_type = variant.variant_type.name
                    variant_item.additional_price = variant.additional_price
        
        return orders

    def get_payable_orders(
        self, 
        db: Session, 
        current_user_id: uuid.UUID, 
        limit: int = 20, 
        offset: int = 0,
        coffee_shop_id: Optional[uuid.UUID] = None
    ):
        """Get orders that can be paid by others (excluding current user's orders)"""
        query = db.query(OrderModel).filter(
            OrderModel.status == OrderStatus.PENDING,  # Only pending orders
            OrderModel.paid_by_user_id.is_(None),  # Not being paid by anyone
            OrderModel.user_id != current_user_id  # Exclude current user's orders
        ).options(
            joinedload(OrderModel.user),
            joinedload(OrderModel.order_items).joinedload(OrderItemModel.coffee).joinedload(CoffeeMenuModel.coffee_shop)
        )
        
        # Filter by coffee shop if specified
        if coffee_shop_id:
            query = query.join(OrderItemModel).join(CoffeeMenuModel).filter(
                CoffeeMenuModel.coffee_shop_id == coffee_shop_id
            )
        
        # Sort by most recent first
        query = query.order_by(desc(OrderModel.ordered_at))
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        orders = query.all()
        
        # Transform to PayableOrderResponse format
        result = []
        for order in orders:
            # Get coffee shop name from first item
            coffee_shop_name = None
            if order.order_items:
                coffee_shop_name = order.order_items[0].coffee.coffee_shop.name
            
            # Create items summary
            items_summary_parts = []
            for item in order.order_items:
                items_summary_parts.append(f"{item.quantity}x {item.coffee.name}")
            items_summary = ", ".join(items_summary_parts)
            
            # Calculate time since order
            time_diff = datetime.utcnow() - order.ordered_at
            if time_diff.days > 0:
                time_since_order = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
            elif time_diff.seconds >= 3600:
                hours = time_diff.seconds // 3600
                time_since_order = f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif time_diff.seconds >= 60:
                minutes = time_diff.seconds // 60
                time_since_order = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                time_since_order = "Just now"
            
            result.append({
                "id": order.id,
                "order_id": order.order_id,
                "total_price": order.total_price,
                "ordered_at": order.ordered_at,
                "user_name": order.user.name,
                "user_email": order.user.email,
                "coffee_shop_name": coffee_shop_name,
                "items_count": len(order.order_items),
                "items_summary": items_summary,
                "time_since_order": time_since_order
            })
        
        return result

    def get_order_by_id(self, db: Session, order_id: uuid.UUID, user_id: uuid.UUID):
        """Get a single order with its items and variants"""
        order = db.query(OrderModel).filter(
            OrderModel.id == order_id,
            or_(
                OrderModel.user_id == user_id,  # Order owner
                OrderModel.paid_by_user_id == user_id  # Person paying for the order
            )
        ).options(
            joinedload(OrderModel.order_items).joinedload(OrderItemModel.coffee),
            joinedload(OrderModel.order_items).joinedload(OrderItemModel.variants).joinedload(OrderItemVariantModel.variant).joinedload(VariantModel.variant_type), # Load variant type
            joinedload(OrderModel.user),
            joinedload(OrderModel.paid_by_user)
        ).first()
        
        if not order:
            return None
        
        # Enrich order items with coffee name and variants with names
        for item in order.order_items:
            # coffee sudah di-load dengan joinedload
            item.coffee_name = item.coffee.name
            item.coffee.image_url = item.coffee.image_url 
            item.coffee.description = item.coffee.description 
            item.coffee.price = item.coffee.price

            for variant_item in item.variants:
                variant = variant_item.variant
                variant_item.name = variant.name
                variant_item.variant_type = variant.variant_type.name # Akses dari relationship
                variant_item.additional_price = variant.additional_price
        
        # Enrich with paid_by_user_name if applicable
        # Relasi sudah di-load
        
        return order

    def cancel_order(self, db: Session, order_id: uuid.UUID, user_id: uuid.UUID):
        """Cancel an order if it's in PENDING state"""
        order = db.query(OrderModel).filter(
            OrderModel.id == order_id,
            OrderModel.user_id == user_id,  # Only order owner can cancel
            OrderModel.status == OrderStatus.PENDING
        ).first()
        
        if not order:
            return False
        
        # Reset paid_by_user_id if someone was about to pay
        order.paid_by_user_id = None
        order.status = OrderStatus.CANCELLED
        db.commit()
        return True

    def get_orders_by_status(self, db: Session, status: OrderStatus, limit: int = 50):
        """Get orders by status - useful for admin/system operations"""
        return db.query(OrderModel).filter(
            OrderModel.status == status
        ).order_by(desc(OrderModel.ordered_at)).limit(limit).all()

    def get_order_statistics(self, db: Session, user_id: uuid.UUID):
        """Get order statistics for a user"""
        # Orders created by user
        orders_created_query = db.query(func.count(OrderModel.id)).filter(
            OrderModel.user_id == user_id
        )
        orders_created = orders_created_query.scalar() or 0

        # Orders paid for others
        orders_paid_for_others_query = db.query(func.count(OrderModel.id)).filter(
            OrderModel.paid_by_user_id == user_id,
            OrderModel.user_id != user_id  # Exclude self-payments
        )
        orders_paid_for_others = orders_paid_for_others_query.scalar() or 0

        # Total amount spent (including paying for others)
        total_spent_query = db.query(func.sum(OrderModel.total_price)).filter(
            OrderModel.user_id == user_id,
            OrderModel.status == OrderStatus.COMPLETED 
        )
        total_spent = total_spent_query.scalar() or 0

        # Orders paid by others for this user
        orders_paid_by_others_query = db.query(func.count(OrderModel.id)).filter(
            OrderModel.user_id == user_id,
            OrderModel.paid_by_user_id != user_id,
            OrderModel.paid_by_user_id.isnot(None),
            OrderModel.status == OrderStatus.COMPLETED
        )
        orders_paid_by_others = orders_paid_by_others_query.scalar() or 0

        # Rata-rata nilai pesanan (dari pesanan yang dibuat oleh user)
        total_revenue_from_created_orders_query = db.query(func.sum(OrderModel.total_price)).filter(
            OrderModel.user_id == user_id,
            OrderModel.status == OrderStatus.COMPLETED
        )
        total_revenue_from_created_orders = total_revenue_from_created_orders_query.scalar() or 0
        
        average_order_value = 0.0
        if orders_created > 0: # Gunakan orders_created untuk menghitung AOV dari pesanan yang dibuat
             average_order_value = total_revenue_from_created_orders / orders_created


        return {
            "orders_created": orders_created,
            "orders_paid_for_others": orders_paid_for_others,
            "orders_paid_by_others": orders_paid_by_others,
            "total_spent": total_spent,
            "average_order_value": round(average_order_value, 2)
        }

# Create singleton instance
order_service = OrderService()