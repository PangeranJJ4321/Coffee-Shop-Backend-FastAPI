"""add_initial_booking_data_single_coffee_shop

Revision ID: 70bf7bc37665
Revises: 10672d139a75
Create Date: 2025-05-29 01:07:46.587476
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime, time
from uuid import uuid4, UUID
import enum

# revision identifiers
revision: str = '70bf7bc37665'
down_revision: Union[str, None] = '10672d139a75'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Enum WeekDay
class WeekDay(enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"

def upgrade():
    single_coffee_shop_id = '8dede67b-7f3c-4c30-9a05-544f8f093bd5'

    # Insert operating hours
    operating_hours = sa.Table(
        'operating_hours',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('day', sa.Enum(WeekDay)),
        sa.Column('opening_time', sa.Time),
        sa.Column('closing_time', sa.Time),
        sa.Column('is_open', sa.Boolean),
        sa.Column('coffee_shop_id', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
    )

    days = [e.value for e in WeekDay]
    operating_hours_data = []
    for day in days:
        opening, closing = {
            "MONDAY": (8, 21),
            "TUESDAY": (8, 21),
            "WEDNESDAY": (8, 21),
            "THURSDAY": (8, 21),
            "FRIDAY": (8, 22),
            "SATURDAY": (9, 23),
            "SUNDAY": (9, 20),
        }[day]
        operating_hours_data.append({
            'id': uuid4(),
            'coffee_shop_id': single_coffee_shop_id,
            'day': day,
            'opening_time': time(opening, 0),
            'closing_time': time(closing, 0),
            'is_open': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        })

    op.bulk_insert(operating_hours, operating_hours_data)

    # Insert time slots
    time_slots = sa.Table(
        'time_slots',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('start_time', sa.Time),
        sa.Column('end_time', sa.Time),
        sa.Column('max_capacity', sa.Integer),
        sa.Column('is_active', sa.Boolean),
        sa.Column('coffee_shop_id', postgresql.UUID(as_uuid=True)),
        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
    )

    time_slots_data = []
    for h in range(7, 23):
        time_slots_data.append({
            'id': uuid4(),
            'coffee_shop_id': single_coffee_shop_id,
            'start_time': time(h, 0),
            'end_time': time(h + 1, 0),
            'max_capacity': 15,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        })
        if h < 22:
            time_slots_data.append({
                'id': uuid4(),
                'coffee_shop_id': single_coffee_shop_id,
                'start_time': time(h, 30),
                'end_time': time(h + 1, 30),
                'max_capacity': 10,
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            })

    op.bulk_insert(time_slots, time_slots_data)

def downgrade():
    single_coffee_shop_id = '8dede67b-7f3c-4c30-9a05-544f8f093bd5'

    op.execute(f"""DELETE FROM time_slots WHERE coffee_shop_id = {single_coffee_shop_id}""")
    op.execute(f"""DELETE FROM operating_hours WHERE coffee_shop_id = {single_coffee_shop_id}""")
    
    # Optional:
    # conn.execute(sa.text("DELETE FROM coffee_shops WHERE id = :id"), {"id": str(single_coffee_shop_id)})
