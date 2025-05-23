"""seed coffee_shops table

Revision ID: 40d2709024b8
Revises: a0b05f0f2c8b
Create Date: 2025-05-23 14:06:04.024390

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '40d2709024b8'
down_revision: Union[str, None] = 'a0b05f0f2c8b'
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
