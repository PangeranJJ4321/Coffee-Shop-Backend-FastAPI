"""Tambah tabel

Revision ID: e7495523c673
Revises: 
Create Date: 2025-06-20 00:39:42.388517

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e7495523c673'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('coffee_shops',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('address', sa.Text(), nullable=False),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('average_rating', sa.Float(), nullable=True),
    sa.Column('total_ratings', sa.Integer(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('roles',
    sa.Column('role', sa.Enum('ADMIN', 'USER', 'GUEST', name='role'), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('role')
    )
    op.create_table('variant_types',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('is_required', sa.Boolean(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('coffee_menus',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('price', sa.Integer(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('image_url', sa.String(), nullable=True),
    sa.Column('is_available', sa.Boolean(), nullable=False),
    sa.Column('average_rating', sa.Float(), nullable=True),
    sa.Column('total_ratings', sa.Integer(), nullable=True),
    sa.Column('long_description', sa.Text(), nullable=True),
    sa.Column('category', sa.String(), nullable=True),
    sa.Column('tags', postgresql.ARRAY(sa.String()), nullable=True),
    sa.Column('preparation_time', sa.String(), nullable=True),
    sa.Column('caffeine_content', sa.String(), nullable=True),
    sa.Column('origin', sa.String(), nullable=True),
    sa.Column('roast_level', sa.String(), nullable=True),
    sa.Column('featured', sa.Boolean(), nullable=False),
    sa.Column('coffee_shop_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['coffee_shop_id'], ['coffee_shops.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_coffee_menus_category'), 'coffee_menus', ['category'], unique=False)
    op.create_table('operating_hours',
    sa.Column('day', sa.Enum('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY', name='weekday'), nullable=False),
    sa.Column('opening_time', sa.Time(), nullable=False),
    sa.Column('closing_time', sa.Time(), nullable=False),
    sa.Column('is_open', sa.Boolean(), nullable=False),
    sa.Column('coffee_shop_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['coffee_shop_id'], ['coffee_shops.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tables',
    sa.Column('table_number', sa.String(), nullable=False),
    sa.Column('capacity', sa.Integer(), nullable=False),
    sa.Column('is_available', sa.Boolean(), nullable=False),
    sa.Column('coffee_shop_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['coffee_shop_id'], ['coffee_shops.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('time_slots',
    sa.Column('start_time', sa.Time(), nullable=False),
    sa.Column('end_time', sa.Time(), nullable=False),
    sa.Column('max_capacity', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('coffee_shop_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['coffee_shop_id'], ['coffee_shops.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.Column('password_hash', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('is_verified', sa.Boolean(), nullable=False),
    sa.Column('verification_token', sa.String(), nullable=True),
    sa.Column('verification_token_expires', sa.DateTime(), nullable=True),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.Column('reset_token', sa.String(), nullable=True),
    sa.Column('reset_token_expires', sa.DateTime(), nullable=True),
    sa.Column('role_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    op.create_table('variants',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('additional_price', sa.Integer(), nullable=False),
    sa.Column('is_available', sa.Boolean(), nullable=False),
    sa.Column('variant_type_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['variant_type_id'], ['variant_types.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('coffee_variants',
    sa.Column('is_default', sa.Boolean(), nullable=False),
    sa.Column('coffee_id', sa.UUID(), nullable=False),
    sa.Column('variant_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['coffee_id'], ['coffee_menus.id'], ),
    sa.ForeignKeyConstraint(['variant_id'], ['variants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('notifications',
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('is_read', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('orders',
    sa.Column('order_id', sa.String(), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'PROCESSING', 'CONFIRMED', 'PREPARING', 'READY', 'DELIVERED', 'COMPLETED', 'CANCELLED', name='orderstatus'), nullable=False),
    sa.Column('total_price', sa.Integer(), nullable=False),
    sa.Column('ordered_at', sa.DateTime(), nullable=False),
    sa.Column('payment_note', sa.Text(), nullable=True),
    sa.Column('paid_at', sa.DateTime(), nullable=True),
    sa.Column('delivery_method', sa.String(), nullable=True),
    sa.Column('recipient_name', sa.String(), nullable=True),
    sa.Column('recipient_phone_number', sa.String(), nullable=True),
    sa.Column('delivery_address', sa.Text(), nullable=True),
    sa.Column('order_notes', sa.Text(), nullable=True),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('paid_by_user_id', sa.UUID(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['paid_by_user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('order_id')
    )
    op.create_table('ratings',
    sa.Column('rating', sa.Integer(), nullable=False),
    sa.Column('review', sa.Text(), nullable=True),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('coffee_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['coffee_id'], ['coffee_menus.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user_favorites',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('coffee_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['coffee_id'], ['coffee_menus.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('bookings',
    sa.Column('booking_id', sa.String(), nullable=False),
    sa.Column('table_count', sa.Integer(), nullable=False),
    sa.Column('guest_count', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('NOCONFIRM', 'CONFIRM', 'SUCCESS', 'CANCELLED', name='bookingstatus'), nullable=False),
    sa.Column('booking_date', sa.DateTime(), nullable=False),
    sa.Column('booking_reminder_sent', sa.Boolean(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('order_id', sa.UUID(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('booking_id')
    )
    op.create_table('order_items',
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('subtotal', sa.Integer(), nullable=False),
    sa.Column('order_id', sa.UUID(), nullable=False),
    sa.Column('coffee_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['coffee_id'], ['coffee_menus.id'], ),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order_status_history',
    sa.Column('order_id', sa.UUID(), nullable=False),
    sa.Column('old_status', sa.Enum('PENDING', 'PROCESSING', 'CONFIRMED', 'PREPARING', 'READY', 'DELIVERED', 'COMPLETED', 'CANCELLED', name='orderstatus'), nullable=True),
    sa.Column('new_status', sa.Enum('PENDING', 'PROCESSING', 'CONFIRMED', 'PREPARING', 'READY', 'DELIVERED', 'COMPLETED', 'CANCELLED', name='orderstatus'), nullable=False),
    sa.Column('changed_by_user_id', sa.UUID(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('changed_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['changed_by_user_id'], ['users.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('transactions',
    sa.Column('transaction_id', sa.String(), nullable=False),
    sa.Column('gross_amount', sa.Integer(), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'SUCCESS', 'FAILED', name='statustype'), nullable=False),
    sa.Column('payment_time', sa.DateTime(), nullable=True),
    sa.Column('expiry_time', sa.DateTime(), nullable=True),
    sa.Column('transaction_time', sa.DateTime(), nullable=False),
    sa.Column('payment_type', sa.String(), nullable=False),
    sa.Column('qr_code_url', sa.Text(), nullable=True),
    sa.Column('deeplink_url', sa.Text(), nullable=True),
    sa.Column('order_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('transaction_id')
    )
    op.create_table('booking_status_history',
    sa.Column('booking_id', sa.UUID(), nullable=False),
    sa.Column('old_status', sa.Enum('NOCONFIRM', 'CONFIRM', 'SUCCESS', 'CANCELLED', name='bookingstatus'), nullable=True),
    sa.Column('new_status', sa.Enum('NOCONFIRM', 'CONFIRM', 'SUCCESS', 'CANCELLED', name='bookingstatus'), nullable=False),
    sa.Column('changed_by_user_id', sa.UUID(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('changed_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['changed_by_user_id'], ['users.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('booking_tables',
    sa.Column('booking_id', sa.UUID(), nullable=False),
    sa.Column('table_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['booking_id'], ['bookings.id'], ),
    sa.ForeignKeyConstraint(['table_id'], ['tables.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order_item_variants',
    sa.Column('order_item_id', sa.UUID(), nullable=False),
    sa.Column('variant_id', sa.UUID(), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['order_item_id'], ['order_items.id'], ),
    sa.ForeignKeyConstraint(['variant_id'], ['variants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('payouts',
    sa.Column('amount', sa.Integer(), nullable=False),
    sa.Column('bank_name', sa.String(), nullable=False),
    sa.Column('account_number', sa.String(), nullable=False),
    sa.Column('account_name', sa.String(), nullable=False),
    sa.Column('reference_id', sa.String(), nullable=False),
    sa.Column('status', sa.Enum('PENDING', 'SUCCESS', 'FAILED', name='statustype'), nullable=False),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('transaction_id', sa.UUID(), nullable=True),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('reference_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('payouts')
    op.drop_table('order_item_variants')
    op.drop_table('booking_tables')
    op.drop_table('booking_status_history')
    op.drop_table('transactions')
    op.drop_table('order_status_history')
    op.drop_table('order_items')
    op.drop_table('bookings')
    op.drop_table('user_favorites')
    op.drop_table('ratings')
    op.drop_table('orders')
    op.drop_table('notifications')
    op.drop_table('coffee_variants')
    op.drop_table('variants')
    op.drop_table('users')
    op.drop_table('time_slots')
    op.drop_table('tables')
    op.drop_table('operating_hours')
    op.drop_index(op.f('ix_coffee_menus_category'), table_name='coffee_menus')
    op.drop_table('coffee_menus')
    op.drop_table('variant_types')
    op.drop_table('roles')
    op.drop_table('coffee_shops')
    # ### end Alembic commands ###
