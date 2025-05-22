"""create coffee_shops table

Revision ID: cc647bc1aafe
Revises: add_password_reset_columns
Create Date: 2025-05-22 19:06:34.332666

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc647bc1aafe'
down_revision: Union[str, None] = 'add_password_reset_columns'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Insert initial data
    op.execute("""
        INSERT INTO coffee_shops (id, name, address, phone_number, image_url, created_at, updated_at)
        VALUES (
            gen_random_uuid(),
            'Coffee Shop',
            'Jalan Aja Sendiri',
            '+6221234567',
            'https://res.cloudinary.com/douoytv3i/image/upload/v1747115500/gosqtbdthecn2pdi0nto.png',
            NOW(),
            NOW()
        )
    """)


def downgrade():
    op.drop_table('coffee_shops')
