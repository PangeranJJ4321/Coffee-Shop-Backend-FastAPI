"""Add payment_type column to transactions table

Revision ID: 2d944a480dcc
Revises: d8226aec4bda
Create Date: 2025-06-02 23:40:04.645925

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column # Tambahkan import ini
from sqlalchemy.dialects import postgresql # untuk UUID jika diperlukan

# revision identifiers, used by Alembic.
revision: str = '2d944a480dcc'
down_revision: Union[str, None] = 'd8226aec4bda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Langkah 1: Tambahkan kolom sebagai nullable terlebih dahulu
    op.add_column('transactions', sa.Column('payment_type', sa.String(), nullable=True))

    # Langkah 2 (Opsional tapi disarankan): Isi nilai default untuk baris yang sudah ada
    # Anda perlu memberikan nilai default yang logis untuk transaksi yang sudah ada.
    # Misalnya, 'UNKNOWN' atau 'DEFAULT'
    bind = op.get_bind()
    session = sa.orm.Session(bind=bind)

    transactions_table = table(
        'transactions',
        column('id', postgresql.UUID(as_uuid=True)), # Sesuaikan tipe data primary key
        column('payment_type', sa.String())
    )

    # Contoh: Mengisi 'UNKNOWN' untuk semua baris yang payment_type-nya masih NULL
    # atau yang ada sebelum kolom ini ditambahkan.
    # Atau, Anda bisa mencoba menebak jenis pembayaran dari data lain jika memungkinkan.
    session.execute(
        transactions_table.update().
        where(transactions_table.c.payment_type == None). # Gunakan == None untuk NULL
        values(payment_type='UNKNOWN_TYPE')
    )
    session.commit() # Komit perubahan ini

    # Langkah 3: Ubah kolom menjadi NOT NULL (setelah semua baris diisi)
    # Hapus 'nullable=False' dari definisi awal kolom
    op.alter_column('transactions', 'payment_type', existing_type=sa.String(), nullable=False)


def downgrade():
    # Dalam downgrade, Anda hanya perlu menghapus kolom.
    # Tidak perlu khawatir tentang nilai NULL di sini karena kolom akan dihapus.
    op.drop_column('transactions', 'payment_type')