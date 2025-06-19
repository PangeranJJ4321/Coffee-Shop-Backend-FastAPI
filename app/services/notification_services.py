"""
Service for sending notifications (email)
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
import os
from jinja2 import Template

from app.models.order import OrderModel, OrderStatus
from app.models.booking import BookingModel, BookingStatus
from app.models.user import UserModel
from app.core.config import settings

class NotificationService:
    def __init__(self):
        self.smtp_server = settings.MAILTRAP_HOST
        self.smtp_port = settings.MAILTRAP_PORT
        self.smtp_username = settings.MAILTRAP_USERNAME
        self.smtp_password = settings.MAILTRAP_PASSWORD
        self.sender_email = settings.EMAILS_FROM_EMAIL
        self.sender_name = settings.EMAILS_FROM_NAME or "CoffeeBooking System"


    async def send_email(self, to_email: str, to_name: str, subject: str, html_content: str, text_content: str = None):
        """Send email notification"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
            msg['To'] = f"{to_name} <{to_email}>"

            # Add text version if provided
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)

            # Add HTML version
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)

            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
                
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False

    async def send_order_status_notification(self, db: Session, order_id: UUID, new_status: OrderStatus, changed_by_user_id: UUID):
        """Send order status change notification to customer"""
        # Get order details
        order = db.query(OrderModel).filter(OrderModel.id == order_id).first()
        if not order:
            return False

        # Get customer details
        customer = db.query(UserModel).filter(UserModel.id == order.user_id).first()
        if not customer:
            return False

        # Get admin who changed the status
        admin = db.query(UserModel).filter(UserModel.id == changed_by_user_id).first()
        admin_name = admin.name if admin else "Admin"

        # Prepare email content based on status
        status_messages = {
            OrderStatus.PENDING: {
                "subject": f"Order {order.order_id} - Received",
                "title": "Order Received",
                "message": "We have received your order and it's being processed.",
                "color": "#fbbf24"  # yellow
            },
            OrderStatus.CONFIRMED: {
                "subject": f"Order {order.order_id} - Confirmed",
                "title": "Order Confirmed",
                "message": "Your order has been confirmed and is being prepared.",
                "color": "#3b82f6"  # blue
            },
            OrderStatus.PREPARING: {
                "subject": f"Order {order.order_id} - Being Prepared",
                "title": "Order Being Prepared",
                "message": "Your delicious coffee is being prepared by our baristas.",
                "color": "#f59e0b"  # orange
            },
            OrderStatus.READY: {
                "subject": f"Order {order.order_id} - Ready for Pickup",
                "title": "Order Ready!",
                "message": "Your order is ready for pickup. Please come to collect it.",
                "color": "#10b981"  # green
            },
            OrderStatus.COMPLETED: {
                "subject": f"Order {order.order_id} - Completed",
                "title": "Order Completed",
                "message": "Thank you! Your order has been completed. We hope you enjoyed it!",
                "color": "#059669"  # dark green
            },
            OrderStatus.CANCELLED: {
                "subject": f"Order {order.order_id} - Cancelled",
                "title": "Order Cancelled",
                "message": "Your order has been cancelled. If you have any questions, please contact us.",
                "color": "#ef4444"  # red
            }
        }

        status_info = status_messages.get(new_status, status_messages[OrderStatus.PENDING])

        # HTML email template
        html_template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ subject }}</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: {{ color }}; color: white; padding: 20px; border-radius: 5px 5px 0 0; }
                .content { background: #f9f9f9; padding: 20px; border-radius: 0 0 5px 5px; }
                .order-details { background: white; padding: 15px; border-radius: 5px; margin: 15px 0; }
                .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{{ title }}</h1>
                </div>
                <div class="content">
                    <p>Dear {{ customer_name }},</p>
                    <p>{{ message }}</p>
                    
                    <div class="order-details">
                        <h3>Order Details:</h3>
                        <p><strong>Order ID:</strong> {{ order_id }}</p>
                        <p><strong>Status:</strong> {{ status }}</p>
                        <p><strong>Total Amount:</strong> Rp {{ total_price:,}}</p>
                        <p><strong>Ordered At:</strong> {{ ordered_at }}</p>
                        {% if coffee_shop_name %}
                        <p><strong>Coffee Shop:</strong> {{ coffee_shop_name }}</p>
                        {% endif %}
                    </div>
                    
                    <p>If you have any questions, please don't hesitate to contact us.</p>
                    <p>Thank you for choosing our service!</p>
                </div>
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>Updated by: {{ admin_name }} at {{ current_time }}</p>
                </div>
            </div>
        </body>
        </html>
        """)

        html_content = html_template.render(
            subject=status_info["subject"],
            title=status_info["title"],
            message=status_info["message"],
            color=status_info["color"],
            customer_name=customer.name,
            order_id=order.order_id,
            status=new_status.value.title(),
            total_price=order.total_price,
            ordered_at=order.ordered_at.strftime("%B %d, %Y at %I:%M %p"),
            coffee_shop_name=getattr(order.coffee_shop, 'name', None) if hasattr(order, 'coffee_shop') else None,
            admin_name=admin_name,
            current_time=datetime.now().strftime("%B %d, %Y at %I:%M %p")
        )

        return await self.send_email(
            to_email=customer.email,
            to_name=customer.name,
            subject=status_info["subject"],
            html_content=html_content
        )

    async def send_booking_status_notification(self, db: Session, booking_id: UUID, new_status: BookingStatus, changed_by_user_id: UUID):
        """Send booking status change notification to customer"""
        # Get booking details
        booking = db.query(BookingModel).filter(BookingModel.id == booking_id).first()
        if not booking:
            return False

        # Get customer details
        customer = db.query(UserModel).filter(UserModel.id == booking.user_id).first()
        if not customer:
            return False

        # Get admin who changed the status
        admin = db.query(UserModel).filter(UserModel.id == changed_by_user_id).first()
        admin_name = admin.name if admin else "System"

        # Prepare email content based on status
        status_messages = {
            BookingStatus.PENDING: {
                "subject": f"Booking {booking.booking_id} - Pending Confirmation",
                "title": "Booking Received",
                "message": "We have received your table booking request and it's being processed.",
                "color": "#fbbf24"
            },
            BookingStatus.CONFIRMED: {
                "subject": f"Booking {booking.booking_id} - Confirmed",
                "title": "Booking Confirmed",
                "message": "Great news! Your table booking has been confirmed.",
                "color": "#10b981"
            },
            BookingStatus.CANCELLED: {
                "subject": f"Booking {booking.booking_id} - Cancelled",
                "title": "Booking Cancelled",
                "message": "Your table booking has been cancelled. If you have any questions, please contact us.",
                "color": "#ef4444"
            },
            BookingStatus.COMPLETED: {
                "subject": f"Booking {booking.booking_id} - Completed",
                "title": "Thank You!",
                "message": "Thank you for dining with us! We hope you had a wonderful experience.",
                "color": "#059669"
            }
        }

        status_info = status_messages.get(new_status, status_messages[BookingStatus.PENDING])

        # HTML email template
        html_template = Template("""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{{ subject }}</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background: {{ color }}; color: white; padding: 20px; border-radius: 5px 5px 0 0; }
                .content { background: #f9f9f9; padding: 20px; border-radius: 0 0 5px 5px; }
                .booking-details { background: white; padding: 15px; border-radius: 5px; margin: 15px 0; }
                .footer { text-align: center; margin-top: 20px; color: #666; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{{ title }}</h1>
                </div>
                <div class="content">
                    <p>Dear {{ customer_name }},</p>
                    <p>{{ message }}</p>
                    
                    <div class="booking-details">
                        <h3>Booking Details:</h3>
                        <p><strong>Booking ID:</strong> {{ booking_id }}</p>
                        <p><strong>Status:</strong> {{ status }}</p>
                        <p><strong>Date & Time:</strong> {{ booking_date }}</p>
                        <p><strong>Guest Count:</strong> {{ guest_count }}</p>
                        <p><strong>Table Count:</strong> {{ table_count }}</p>
                        {% if coffee_shop_name %}
                        <p><strong>Coffee Shop:</strong> {{ coffee_shop_name }}</p>
                        {% endif %}
                    </div>
                    
                    {% if new_status == 'CONFIRMED' %}
                    <div style="background: #d1fae5; padding: 15px; border-radius: 5px; margin: 15px 0;">
                        <p><strong>Important Reminders:</strong></p>
                        <ul>
                            <li>Please arrive on time for your reservation</li>
                            <li>If you need to cancel or modify your booking, please contact us at least 2 hours in advance</li>
                            <li>Late arrivals may result in table reassignment</li>
                        </ul>
                    </div>
                    {% endif %}
                    
                    <p>If you have any questions, please don't hesitate to contact us.</p>
                    <p>Thank you for choosing our service!</p>
                </div>
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                    <p>Updated by: {{ admin_name }} at {{ current_time }}</p>
                </div>
            </div>
        </body>
        </html>
        """)

        html_content = html_template.render(
            subject=status_info["subject"],
            title=status_info["title"],
            message=status_info["message"],
            color=status_info["color"],
            customer_name=customer.name,
            booking_id=booking.booking_id,
            status=new_status.value.title(),
            booking_date=booking.booking_date.strftime("%B %d, %Y at %I:%M %p"),
            guest_count=booking.guest_count,
            table_count=booking.table_count,
            coffee_shop_name=getattr(booking.coffee_shop, 'name', None) if hasattr(booking, 'coffee_shop') else None,
            admin_name=admin_name,
            current_time=datetime.now().strftime("%B %d, %Y at %I:%M %p"),
            new_status=new_status.value
        )

        return await self.send_email(
            to_email=customer.email,
            to_name=customer.name,
            subject=status_info["subject"],
            html_content=html_content
        )

# Create instance
notification_service = NotificationService()