"""pay for others support

Revision ID: a0b05f0f2c8b
Revises: 9e139ec6c5f4
Create Date: 2025-05-23 14:03:53.242480

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0b05f0f2c8b'
down_revision: Union[str, None] = '9e139ec6c5f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Add comment to column (if not already added in model)
    op.execute("""
        COMMENT ON COLUMN orders.paid_by_user_id IS 
        'User ID of who is paying for this order. NULL means order owner will pay. Same as user_id means self-payment.';
    """)

    # Create indexes
    op.create_index(
        'idx_orders_paid_by_user_id', 'orders', ['paid_by_user_id'], unique=False
    )

    op.create_index(
        'idx_orders_payable',
        'orders',
        ['status', 'paid_by_user_id'],
        unique=False,
        postgresql_where=sa.text("status = 'PENDING' AND paid_by_user_id IS NULL")
    )

    op.create_index(
        'idx_orders_user_or_payer',
        'orders',
        ['user_id', 'paid_by_user_id'],
        unique=False
    )

    # Update data for completed orders
    op.execute("""
        UPDATE orders 
        SET paid_by_user_id = user_id 
        WHERE status = 'COMPLETED' AND paid_by_user_id IS NULL;
    """)

    # Optional constraint: prevent user from paying their own order via pay-for-others
    # Uncomment if you want to enforce at DB level
    # op.execute("""
    #     ALTER TABLE orders ADD CONSTRAINT chk_no_self_pay_for_others
    #     CHECK (user_id != paid_by_user_id OR paid_by_user_id IS NULL);
    # """)


def downgrade():
    # Remove everything added in upgrade
    op.drop_index('idx_orders_user_or_payer', table_name='orders')
    op.drop_index('idx_orders_payable', table_name='orders')
    op.drop_index('idx_orders_paid_by_user_id', table_name='orders')

    op.execute("COMMENT ON COLUMN orders.paid_by_user_id IS NULL")

    # If you added the constraint, also drop it here:
    # op.execute("ALTER TABLE orders DROP CONSTRAINT chk_no_self_pay_for_others")


