"""add_initial_booking_data_single_coffee_shop

Revision ID: 7f868d964e3d
Revises: 460c252a14fb
Create Date: 2025-05-29 00:28:06.970550

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime, time
from uuid import uuid4
import enum


# revision identifiers, used by Alembic.
revision: str = '7f868d964e3d'
down_revision: Union[str, None] = '460c252a14fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# revision identifiers, used by Alembic.
revision = 'xxxxxxxxxxxx' # Ganti dengan ID revisi Anda
down_revision = '<previous_revision_id>' # Ganti dengan ID revisi sebelumnya
branch_labels = None
depends_on = None

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
    
    # --- Dapatkan Coffee Shop IDs yang ada ---
    # Asumsi Anda sudah memiliki data di tabel coffee_shops
    # Jika belum, Anda harus membuatnya terlebih dahulu (misalnya di migrasi terpisah)
    # Atau tambahkan data coffee shop dummy di sini juga jika ini migrasi pertama.
    
    # Contoh mendapatkan 2 coffee_shop_id yang ada (sesuaikan dengan data Anda)
    # Jika tidak ada, Anda bisa menambahkannya di sini.
    
    coffee_shop_results = conn.execute(sa.text("SELECT id FROM coffee_shops LIMIT 2")).fetchall()
    
    if not coffee_shop_results:
        print("No coffee shops found. Creating dummy coffee shops for seeding.")
        # Buat dummy coffee shops jika tidak ada
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
                'id': uuid4(),
                'name': 'Central Perk Cafe',
                'address': '123 Main Street',
                'phone_number': '+11234567890',
                'email': 'info@centralperk.com',
                'website': 'http://centralperk.com',
                'description': 'The iconic coffee shop from Friends.',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            },
            {
                'id': uuid4(),
                'name': 'The Daily Grind',
                'address': '456 Elm Avenue',
                'phone_number': '+19876543210',
                'email': 'hello@dailygrind.com',
                'website': 'http://dailygrind.com',
                'description': 'Your daily dose of caffeine.',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            }
        ])
        coffee_shop_results = conn.execute(sa.text("SELECT id FROM coffee_shops LIMIT 2")).fetchall()


    coffee_shop_ids = [row[0] for row in coffee_shop_results]

    if not coffee_shop_ids:
        print("Error: Could not find or create coffee shop IDs. Skipping operating_hours and time_slots seeding.")
        return # Keluar dari fungsi upgrade jika tidak ada coffee shop IDs
    
    # --- Seed Data for OperatingHoursModel ---
    operating_hours_data = []
    days = [e.value for e in WeekDay] # ['MONDAY', 'TUESDAY', ...]

    # Untuk Coffee Shop pertama
    cs1_id = coffee_shop_ids[0]
    # Buka Senin-Jumat, tutup Sabtu-Minggu
    for day in days:
        if day in ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]:
            operating_hours_data.append({
                'id': uuid4(),
                'coffee_shop_id': cs1_id,
                'day': day,
                'opening_time': time(8, 0),
                'closing_time': time(21, 0),
                'is_open': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            })
        else: # Weekend closed
            operating_hours_data.append({
                'id': uuid4(),
                'coffee_shop_id': cs1_id,
                'day': day,
                'opening_time': time(0, 0), # Placeholder, actual closing time irrelevant if not open
                'closing_time': time(0, 0),
                'is_open': False,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            })
    
    # Untuk Coffee Shop kedua (jika ada)
    if len(coffee_shop_ids) > 1:
        cs2_id = coffee_shop_ids[1]
        # Buka setiap hari dengan jam bervariasi
        operating_hours_data.append({
            'id': uuid4(),
            'coffee_shop_id': cs2_id,
            'day': WeekDay.MONDAY.value,
            'opening_time': time(7, 30),
            'closing_time': time(20, 0),
            'is_open': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        })
        operating_hours_data.append({
            'id': uuid4(),
            'coffee_shop_id': cs2_id,
            'day': WeekDay.TUESDAY.value,
            'opening_time': time(7, 30),
            'closing_time': time(20, 0),
            'is_open': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        })
        operating_hours_data.append({
            'id': uuid4(),
            'coffee_shop_id': cs2_id,
            'day': WeekDay.WEDNESDAY.value,
            'opening_time': time(7, 30),
            'closing_time': time(20, 0),
            'is_open': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        })
        operating_hours_data.append({
            'id': uuid4(),
            'coffee_shop_id': cs2_id,
            'day': WeekDay.THURSDAY.value,
            'opening_time': time(7, 30),
            'closing_time': time(20, 0),
            'is_open': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        })
        operating_hours_data.append({
            'id': uuid4(),
            'coffee_shop_id': cs2_id,
            'day': WeekDay.FRIDAY.value,
            'opening_time': time(7, 30),
            'closing_time': time(22, 0), # Late close on Friday
            'is_open': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        })
        operating_hours_data.append({
            'id': uuid4(),
            'coffee_shop_id': cs2_id,
            'day': WeekDay.SATURDAY.value,
            'opening_time': time(9, 0),
            'closing_time': time(23, 0), # Longer hours on Saturday
            'is_open': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        })
        operating_hours_data.append({
            'id': uuid4(),
            'coffee_shop_id': cs2_id,
            'day': WeekDay.SUNDAY.value,
            'opening_time': time(9, 0),
            'closing_time': time(18, 0),
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

    # Time slots for Coffee Shop 1 (Central Perk Cafe) - weekdays 8:00 - 21:00
    for h in range(8, 21): # From 8 AM to 8 PM (end_time 21:00)
        time_slots_data.append({
            'id': uuid4(),
            'coffee_shop_id': cs1_id,
            'start_time': time(h, 0),
            'end_time': time(h + 1, 0),
            'max_capacity': 15, # Default capacity per slot
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        })
        # Tambah slot 30 menit
        time_slots_data.append({
            'id': uuid4(),
            'coffee_shop_id': cs1_id,
            'start_time': time(h, 30),
            'end_time': time(h + 1, 30),
            'max_capacity': 10, # Slightly smaller capacity for 30-min slots
            'is_active': True,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        })

    # Time slots for Coffee Shop 2 (The Daily Grind) - daily with varying hours
    if len(coffee_shop_ids) > 1:
        for h in range(7, 23): # From 7 AM to 10 PM (end_time 23:00)
            time_slots_data.append({
                'id': uuid4(),
                'coffee_shop_id': cs2_id,
                'start_time': time(h, 0),
                'end_time': time(h + 1, 0),
                'max_capacity': 12, # Default capacity per slot
                'is_active': True,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            })
            if h < 22: # Prevent 22:30-23:30 slot if closing at 23:00
                time_slots_data.append({
                    'id': uuid4(),
                    'coffee_shop_id': cs2_id,
                    'start_time': time(h, 30),
                    'end_time': time(h + 1, 30),
                    'max_capacity': 8, # Slightly smaller capacity
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

    # Get the coffee shop IDs that were used for seeding
    coffee_shop_results = conn.execute(sa.text("SELECT id FROM coffee_shops LIMIT 2")).fetchall()
    coffee_shop_ids = [str(row[0]) for row in coffee_shop_results] # Convert UUID to string for IN clause

    if coffee_shop_ids:
        # Hapus data time_slots berdasarkan coffee_shop_id
        op.execute(sa.text(f"DELETE FROM time_slots WHERE coffee_shop_id IN ('{','.join(coffee_shop_ids)}')"))
        # Hapus data operating_hours berdasarkan coffee_shop_id
        op.execute(sa.text(f"DELETE FROM operating_hours WHERE coffee_shop_id IN ('{','.join(coffee_shop_ids)}')"))
    
        # Optional: Hapus dummy coffee shops jika Anda membuatnya di upgrade()
        # op.execute(sa.text(f"DELETE FROM coffee_shops WHERE id IN ('{','.join(coffee_shop_ids)}')"))

