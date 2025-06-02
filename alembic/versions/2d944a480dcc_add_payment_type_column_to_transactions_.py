"""Add payment_type column to transactions table

Revision ID: 2d944a480dcc
Revises: d8226aec4bda
Create Date: 2025-06-02 23:40:04.645925

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d944a480dcc'
down_revision: Union[str, None] = 'd8226aec4bda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Menambahkan kolom 'payment_type' ke tabel 'transactions'
    op.add_column('transactions', sa.Column('payment_type', sa.String(), nullable=False))


def downgrade():
    # Menghapus kolom 'payment_type' dari tabel 'transactions'
    op.drop_column('transactions', 'payment_type')