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
from uuid import uuid4
import enum


# revision identifiers, used by Alembic.
revision: str = '70bf7bc37665'
down_revision: Union[str, None] = '10672d139a75'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Pastikan WeekDay enum Anda tersedia untuk Alembic
class WeekDay(enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"

def upgrade():
    # Mendapatkan koneksi dan objek table dari op
    conn = op.get_bind()
    
    # --- Single Coffee Shop ID ---
    # Gunakan ID coffee shop yang Anda berikan
    single_coffee_shop_id = sa.UUID('8dede67b-7f3c-4c30-9a05-544f8f093bd5')

    # Optional: Pastikan coffee shop dengan ID ini ada.
    # Jika Anda yakin ID ini sudah ada di DB Anda, bagian ini bisa dihilangkan.
    # Jika tidak, ini akan mencoba membuatnya.
    existing_coffee_shop = conn.execute(sa.text(f"SELECT id FROM coffee_shops WHERE id = '{single_coffee_shop_id}'")).fetchone()
    
    if not existing_coffee_shop:
        print(f"Coffee shop with ID {single_coffee_shop_id} not found. Creating it now.")
        op.bulk_insert(sa.Table(
            'coffee_shops', sa.MetaData(),
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('name', sa.String),
            sa.Column('address', sa.String),
            sa.Column('phone_number', sa.String),
            sa.Column('email', sa.String),
            sa.Column('website', sa.String),
            sa.Column('description', sa.String),
            sa.Column('created_at', sa.DateTime),
            sa.Column('updated_at', sa.DateTime),
        ), [
            {
                'id': single_coffee_shop_id,
                'name': 'My Single Awesome Coffee Shop',
                'address': '123 Unique Street, Central City',
                'phone_number': '+6281234567890',
                'email': 'info@singlecoffeeshop.com',
                'website': 'http://singlecoffeeshop.com',
                'description': 'The one and only best coffee shop.',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            }
        ])

    # --- Seed Data for OperatingHoursModel ---
    operating_hours_data = []
    days = [e.value for e in WeekDay] # ['MONDAY', 'TUESDAY', ...]

    # Atur jam operasional untuk semua hari (contoh, buka setiap hari)
    for day in days:
        if day in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY"]:
            operating_hours_data.append({
                'id': uuid4(),
                'coffee_shop_id': single_coffee_shop_id,
                'day': day,
                'opening_time': time(8, 0),
                'closing_time': time(21, 0),
                'is_open': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            })
        elif day == "FRIDAY": # Lebih malam di hari Jumat
             operating_hours_data.append({
                'id': uuid4(),
                'coffee_shop_id': single_coffee_shop_id,
                'day': day,
                'opening_time': time(8, 0),
                'closing_time': time(22, 0),
                'is_open': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            })
        elif day == "SATURDAY": # Buka lebih siang, tutup lebih malam
             operating_hours_data.append({
                'id': uuid4(),
                'coffee_shop_id': single_coffee_shop_id,
                'day': day,
                'opening_time': time(9, 0),
                'closing_time': time(23, 0),
                'is_open': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            })
        elif day == "SUNDAY": # Buka lebih siang, tutup lebih awal
             operating_hours_data.append({
                'id': uuid4(),
                'coffee_shop_id': single_coffee_shop_id,
                'day': day,
                'opening_time': time(9, 0),
                'closing_time': time(20, 0),
                'is_open': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            })


    op.bulk_insert(
        sa.Table(
            'operating_hours', sa.MetaData(),
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('day', sa.Enum(WeekDay)),
            sa.Column('opening_time', sa.Time),
            sa.Column('closing_time', sa.Time),
            sa.Column('is_open', sa.Boolean),
            sa.Column('coffee_shop_id', postgresql.UUID(as_uuid=True)),
            sa.Column('created_at', sa.DateTime),
            sa.Column('updated_at', sa.DateTime),
        ),
        operating_hours_data
    )

    # --- Seed Data for TimeSlotModel ---
    time_slots_data = []

    # Time slots dari 08:00 sampai 23:00 (untuk mencakup jam operasional terlebar)
    for h in range(7, 23): # Mulai dari 7 pagi untuk slot awal yang mungkin ada di hari tertentu
        # Slot per jam
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
        # Slot per 30 menit (kecuali di akhir hari untuk menghindari end_time > 23:00)
        if h < 22: # Pastikan end_time tidak melebihi 23:00
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

    op.bulk_insert(
        sa.Table(
            'time_slots', sa.MetaData(),
            sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
            sa.Column('start_time', sa.Time),
            sa.Column('end_time', sa.Time),
            sa.Column('max_capacity', sa.Integer),
            sa.Column('is_active', sa.Boolean),
            sa.Column('coffee_shop_id', postgresql.UUID(as_uuid=True)),
            sa.Column('created_at', sa.DateTime),
            sa.Column('updated_at', sa.DateTime),
        ),
        time_slots_data
    )

def downgrade():
    conn = op.get_bind()
    single_coffee_shop_id = sa.UUID('8dede67b-7f3c-4c30-9a05-544f8f093bd5')

    # Hapus data time_slots dan operating_hours untuk coffee_shop_id ini
    op.execute(sa.text(f"DELETE FROM time_slots WHERE coffee_shop_id = '{single_coffee_shop_id}'"))
    op.execute(sa.text(f"DELETE FROM operating_hours WHERE coffee_shop_id = '{single_coffee_shop_id}'"))
    
    # Optional: Jika Anda ingin menghapus juga dummy coffee shop yang mungkin dibuat oleh upgrade()
    # op.execute(sa.text(f"DELETE FROM coffee_shops WHERE id = '{single_coffee_shop_id}'"))

