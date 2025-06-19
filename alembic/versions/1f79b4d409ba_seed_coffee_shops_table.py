"""seed coffee_shops table

Revision ID: 1f79b4d409ba
Revises: e7495523c673'
Create Date: 2025-05-29 00:52:37.306664

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID # Import UUID
import uuid # Import uuid

# revision identifiers, used by Alembic.
revision: str = '1f79b4d409ba'
down_revision: Union[str, None] = 'e7495523c673'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Definisikan tabel untuk seeding
    coffee_shops_table = sa.table(
        'coffee_shops',
        sa.column('id', UUID),
        sa.column('name', sa.String),
        sa.column('address', sa.Text), # Ubah ke Text jika di model Text
        sa.column('phone_number', sa.String),
        sa.column('image_url', sa.String),
        sa.column('description', sa.String), # Tambahkan description jika ada di model
        sa.column('average_rating', sa.Float), # Tambahkan kolom baru
        sa.column('total_ratings', sa.Integer), # Tambahkan kolom baru
        sa.column('created_at', sa.DateTime),
        sa.column('updated_at', sa.DateTime)
    )

    # Dapatkan timestamp saat ini
    from datetime import datetime
    now = datetime.utcnow()

    # Data seed untuk coffee_shops
    # Menggunakan ID yang sama dengan coffee_shop_id di seed menu items
    shop_id_for_seed = 'ed634a6f-c12d-4ed4-8975-1926a2ee4a43' 
    
    coffee_shop_data = [{
        'id': shop_id_for_seed,
        'name': 'Ngopi Yuk!',
        'address': 'Jalan Kenangan No. 45, Kopi Hangat, Jakarta',
        'phone_number': '+6281234567890',
        'image_url': 'https://res.cloudinary.com/douoytv3i/image/upload/v1717115500/coffee_shop_hero_example.jpg', # Ganti dengan URL gambar asli Anda
        'description': 'Tempat terbaik untuk menikmati kopi spesial dan suasana nyaman.',
        'average_rating': 4.5, # Default rating
        'total_ratings': 100,  # Default total ratings
        'created_at': now,
        'updated_at': now
    }]

    op.bulk_insert(coffee_shops_table, coffee_shop_data)


def downgrade():
    op.execute("DELETE FROM coffee_shops WHERE id = 'ed634a6f-c12d-4ed4-8975-1926a2ee4a43'") # Hapus berdasarkan ID
    # Atau jika ingin drop table, pastikan tidak ada foreign key yang menunjuk ke sana dulu
    # op.drop_table('coffee_shops')