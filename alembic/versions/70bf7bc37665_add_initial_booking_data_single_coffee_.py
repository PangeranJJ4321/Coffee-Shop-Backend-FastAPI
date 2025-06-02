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
    # Do NOT redefine the table here. Assume it already exists from a previous migration.
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
            'coffee_shop_id': UUID(single_coffee_shop_id), # Ensure UUID object for insertion
            'day': day,
            'opening_time': time(opening, 0),
            'closing_time': time(closing, 0),
            'is_open': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        })

    # Use a connection to bulk insert
    conn = op.get_bind()
    for data in operating_hours_data:
        conn.execute(
            sa.text(
                "INSERT INTO operating_hours (id, day, opening_time, closing_time, is_open, coffee_shop_id, created_at, updated_at) "
                "VALUES (:id, :day, :opening_time, :closing_time, :is_open, :coffee_shop_id, :created_at, :updated_at)"
            ),
            data
        )

    # Insert time slots
    # Do NOT redefine the table here. Assume it already exists.
    time_slots_data = []
    for h in range(7, 23):
        time_slots_data.append({
            'id': uuid4(),
            'coffee_shop_id': UUID(single_coffee_shop_id), # Ensure UUID object for insertion
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
                'coffee_shop_id': UUID(single_coffee_shop_id), # Ensure UUID object for insertion
                'start_time': time(h, 30),
                'end_time': time(h + 1, 30),
                'max_capacity': 10,
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            })

    # Use a connection to bulk insert
    for data in time_slots_data:
        conn.execute(
            sa.text(
                "INSERT INTO time_slots (id, start_time, end_time, max_capacity, is_active, coffee_shop_id, created_at, updated_at) "
                "VALUES (:id, :start_time, :end_time, :max_capacity, :is_active, :coffee_shop_id, :created_at, :updated_at)"
            ),
            data
        )

def downgrade():
    single_coffee_shop_id = '8dede67b-7f3c-4c30-9a05-544f8f093bd5'

    conn = op.get_bind()
    conn.execute(sa.text(f"DELETE FROM time_slots WHERE coffee_shop_id = '{single_coffee_shop_id}'"))
    conn.execute(sa.text(f"DELETE FROM operating_hours WHERE coffee_shop_id = '{single_coffee_shop_id}'"))
    
    # Optional:
    # conn.execute(sa.text("DELETE FROM coffee_shops WHERE id = :id"), {"id": str(single_coffee_shop_id)})