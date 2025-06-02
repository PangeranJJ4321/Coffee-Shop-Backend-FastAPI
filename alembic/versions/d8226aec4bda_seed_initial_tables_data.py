"""Seed initial tables data

Revision ID: d8226aec4bda
Revises: 70bf7bc37665
Create Date: 2025-06-02 20:01:09.202942

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql 
import uuid
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = 'd8226aec4bda'
down_revision: Union[str, None] = '70bf7bc37665'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

tables_table = sa.Table(
    'tables',
    sa.MetaData(),
    sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
    sa.Column('table_number', sa.String(255), nullable=False), # Assuming default string length, adjust if needed
    sa.Column('capacity', sa.Integer, nullable=False),
    sa.Column('is_available', sa.Boolean, nullable=False),
    sa.Column('coffee_shop_id', postgresql.UUID(as_uuid=True), sa.ForeignKey("coffee_shops.id"), nullable=False),
    sa.Column('created_at', sa.DateTime, nullable=False),
    sa.Column('updated_at', sa.DateTime, nullable=False),
)

COFFEE_SHOP_ID = '8dede67b-7f3c-4c30-9a05-544f8f093bd5'

def upgrade():
    tables_to_insert = []

    # Tables with capacity 2 (5 tables: A1 to A5)
    for i in range(1, 6):
        tables_to_insert.append({
            'id': uuid.uuid4(),
            'table_number': f'A{i}',
            'capacity': 2,
            'is_available': True,
            'coffee_shop_id': COFFEE_SHOP_ID,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })

    # Tables with capacity 4 (5 tables: B1 to B5)
    for i in range(1, 6):
        tables_to_insert.append({
            'id': uuid.uuid4(),
            'table_number': f'B{i}',
            'capacity': 4,
            'is_available': True,
            'coffee_shop_id': COFFEE_SHOP_ID,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })

    # Tables with capacity 6 (3 tables: C1 to C3)
    for i in range(1, 4):
        tables_to_insert.append({
            'id': uuid.uuid4(),
            'table_number': f'C{i}',
            'capacity': 6,
            'is_available': True,
            'coffee_shop_id': COFFEE_SHOP_ID,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })

    # Tables with capacity 8 (2 tables: D1 to D2)
    for i in range(1, 3):
        tables_to_insert.append({
            'id': uuid.uuid4(),
            'table_number': f'D{i}',
            'capacity': 8,
            'is_available': True,
            'coffee_shop_id': COFFEE_SHOP_ID,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })

    # Total tables: 5 + 5 + 3 + 2 = 15 tables

    op.bulk_insert(tables_table, tables_to_insert)

def downgrade():
    # Delete the seeded data associated with the specific coffee_shop_id
    op.execute(
        tables_table.delete().where(tables_table.c.coffee_shop_id == COFFEE_SHOP_ID)
    )
