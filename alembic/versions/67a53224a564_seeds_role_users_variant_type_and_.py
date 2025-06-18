"""seeds role users, variant type and variant coffee

Revision ID: 67a53224a564
Revises: 1f79b4d409ba'
Create Date: 2025-05-29 00:55:39.206534

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Boolean, Integer, Text, DateTime # Import DateTime jika belum
from sqlalchemy.dialects.postgresql import UUID # Import UUID jika belum


# revision identifiers, used by Alembic.
revision: str = '67a53224a564'
down_revision: Union[str, None] = '1f79b4d409ba'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """Seed initial reference data"""
    
    # Define table structures for seeding
    roles_table = table('roles',
        column('id', UUID),
        column('role', String),
        column('created_at', sa.DateTime),
        column('updated_at', sa.DateTime)
    )
    
    variant_types_table = table('variant_types',
        column('id', UUID),
        column('name', String),
        column('description', Text), 
        column('is_required', Boolean),
        column('created_at', sa.DateTime),
        column('updated_at', sa.DateTime)
    )
    
    variants_table = table('variants',
        column('id', UUID),
        column('name', String),
        column('additional_price', Integer),
        column('is_available', Boolean),
        column('variant_type_id', UUID),
        column('created_at', sa.DateTime),
        column('updated_at', sa.DateTime)
    )
    
    # Get current timestamp
    from datetime import datetime
    now = datetime.utcnow()
    
    # Seed Roles
    # Tambahkan Role USER
    admin_role_id = str(uuid.uuid4())
    guest_role_id = str(uuid.uuid4())

    roles_data = [
        {
            'id': admin_role_id,
            'role': 'ADMIN',
            'created_at': now,
            'updated_at': now
        },
        {
            'id': guest_role_id,
            'role': 'GUEST',
            'created_at': now,
            'updated_at': now
        }
    ]
    
    op.bulk_insert(roles_table, roles_data)
    
    # Seed Variant Types and Variants
    size_type_id = str(uuid.uuid4())
    sugar_type_id = str(uuid.uuid4())
    milk_type_id = str(uuid.uuid4())
    temp_type_id = str(uuid.uuid4())

    variant_types_data = [
        { 'id': size_type_id, 'name': 'Size', 'description': 'Ukuran minuman', 'is_required': True, 'created_at': now, 'updated_at': now },
        { 'id': sugar_type_id, 'name': 'Sugar Level', 'description': 'Tingkat kemanisan', 'is_required': True, 'created_at': now, 'updated_at': now }, # Umumnya sugar level wajib dipilih
        { 'id': milk_type_id, 'name': 'Milk Type', 'description': 'Jenis susu', 'is_required': False, 'created_at': now, 'updated_at': now },
        { 'id': temp_type_id, 'name': 'Temperature', 'description': 'Suhu minuman', 'is_required': True, 'created_at': now, 'updated_at': now }
    ]
    
    op.bulk_insert(variant_types_table, variant_types_data)
    
    # Simpan ID variant types untuk seeding variants
    # Gunakan dictionary untuk memudahkan akses
    variant_type_ids_map = {vt['name']: vt['id'] for vt in variant_types_data}

    # Seed Variants
    variants_data = [
        # Size variants
        {'id': str(uuid.uuid4()), 'name': 'Small', 'additional_price': 0, 'is_available': True, 'variant_type_id': variant_type_ids_map['Size'], 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'Medium', 'additional_price': 3000, 'is_available': True, 'variant_type_id': variant_type_ids_map['Size'], 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'Large', 'additional_price': 5000, 'is_available': True, 'variant_type_id': variant_type_ids_map['Size'], 'created_at': now, 'updated_at': now},
        
        # Sugar level variants
        {'id': str(uuid.uuid4()), 'name': 'No Sugar', 'additional_price': 0, 'is_available': True, 'variant_type_id': variant_type_ids_map['Sugar Level'], 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'Less Sugar', 'additional_price': 0, 'is_available': True, 'variant_type_id': variant_type_ids_map['Sugar Level'], 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'Normal Sugar', 'additional_price': 0, 'is_available': True, 'variant_type_id': variant_type_ids_map['Sugar Level'], 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'Extra Sugar', 'additional_price': 0, 'is_available': True, 'variant_type_id': variant_type_ids_map['Sugar Level'], 'created_at': now, 'updated_at': now},
        
        # Milk type variants
        {'id': str(uuid.uuid4()), 'name': 'Regular Milk', 'additional_price': 0, 'is_available': True, 'variant_type_id': variant_type_ids_map['Milk Type'], 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'Oat Milk', 'additional_price': 5000, 'is_available': True, 'variant_type_id': variant_type_ids_map['Milk Type'], 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'Almond Milk', 'additional_price': 5000, 'is_available': True, 'variant_type_id': variant_type_ids_map['Milk Type'], 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'Soy Milk', 'additional_price': 3000, 'is_available': True, 'variant_type_id': variant_type_ids_map['Milk Type'], 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'No Milk', 'additional_price': 0, 'is_available': True, 'variant_type_id': variant_type_ids_map['Milk Type'], 'created_at': now, 'updated_at': now},
        
        # Temperature variants
        {'id': str(uuid.uuid4()), 'name': 'Hot', 'additional_price': 0, 'is_available': True, 'variant_type_id': variant_type_ids_map['Temperature'], 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'Cold', 'additional_price': 0, 'is_available': True, 'variant_type_id': variant_type_ids_map['Temperature'], 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'Extra Hot', 'additional_price': 0, 'is_available': True, 'variant_type_id': variant_type_ids_map['Temperature'], 'created_at': now, 'updated_at': now},
    ]
    
    op.bulk_insert(variants_table, variants_data)


def downgrade():
    """Remove seeded data"""
    # Delete in reverse order to respect foreign key constraints
    op.execute("DELETE FROM variants")
    op.execute("DELETE FROM variant_types")
    op.execute("DELETE FROM roles")