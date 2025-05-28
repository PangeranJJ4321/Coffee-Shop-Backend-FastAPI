"""seeds role users, variant type and variant coffee

Revision ID: 9e139ec6c5f4
Revises: 70ec36810670
Create Date: 2025-05-23 13:54:07.570238

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column, insert
from sqlalchemy import String, Boolean, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
import uuid

# revision identifiers, used by Alembic.
revision: str = '9e139ec6c5f4'
down_revision: Union[str, None] = '70ec36810670'
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
    roles_data = [
        {
            'id': str(uuid.uuid4()),
            'role': 'ADMIN',
            'created_at': now,
            'updated_at': now
        },
        {
            'id': str(uuid.uuid4()),
            'role': 'GUEST',
            'created_at': now,
            'updated_at': now
        }
    ]
    
    op.bulk_insert(roles_table, roles_data)
    
    # Seed Variant Types and Variants
    variant_types_data = [
        {
            'id': str(uuid.uuid4()),
            'name': 'Size',
            'description': 'Coffee size options',
            'is_required': True,
            'created_at': now,
            'updated_at': now
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Sugar Level',
            'description': 'Sugar level preferences',
            'is_required': False,
            'created_at': now,
            'updated_at': now
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Milk Type',
            'description': 'Type of milk',
            'is_required': False,
            'created_at': now,
            'updated_at': now
        },
        {
            'id': str(uuid.uuid4()),
            'name': 'Temperature',
            'description': 'Drink temperature',
            'is_required': True,
            'created_at': now,
            'updated_at': now
        }
    ]
    
    op.bulk_insert(variant_types_table, variant_types_data)
    
    # Get IDs for variant types (we need to use the same IDs we just created)
    size_id = variant_types_data[0]['id']
    sugar_id = variant_types_data[1]['id']
    milk_id = variant_types_data[2]['id']
    temp_id = variant_types_data[3]['id']
    
    # Seed Variants
    variants_data = [
        # Size variants
        {'id': str(uuid.uuid4()), 'name': 'Small', 'additional_price': 0, 'is_available': True, 'variant_type_id': size_id, 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'Medium', 'additional_price': 3000, 'is_available': True, 'variant_type_id': size_id, 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'Large', 'additional_price': 5000, 'is_available': True, 'variant_type_id': size_id, 'created_at': now, 'updated_at': now},
        
        # Sugar level variants
        {'id': str(uuid.uuid4()), 'name': 'No Sugar', 'additional_price': 0, 'is_available': True, 'variant_type_id': sugar_id, 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'Less Sugar', 'additional_price': 0, 'is_available': True, 'variant_type_id': sugar_id, 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'Normal Sugar', 'additional_price': 0, 'is_available': True, 'variant_type_id': sugar_id, 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'Extra Sugar', 'additional_price': 0, 'is_available': True, 'variant_type_id': sugar_id, 'created_at': now, 'updated_at': now},
        
        # Milk type variants
        {'id': str(uuid.uuid4()), 'name': 'Regular Milk', 'additional_price': 0, 'is_available': True, 'variant_type_id': milk_id, 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'Oat Milk', 'additional_price': 5000, 'is_available': True, 'variant_type_id': milk_id, 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'Almond Milk', 'additional_price': 5000, 'is_available': True, 'variant_type_id': milk_id, 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'Soy Milk', 'additional_price': 3000, 'is_available': True, 'variant_type_id': milk_id, 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'No Milk', 'additional_price': 0, 'is_available': True, 'variant_type_id': milk_id, 'created_at': now, 'updated_at': now},
        
        # Temperature variants
        {'id': str(uuid.uuid4()), 'name': 'Hot', 'additional_price': 0, 'is_available': True, 'variant_type_id': temp_id, 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'Cold', 'additional_price': 0, 'is_available': True, 'variant_type_id': temp_id, 'created_at': now, 'updated_at': now},
        {'id': str(uuid.uuid4()), 'name': 'Extra Hot', 'additional_price': 0, 'is_available': True, 'variant_type_id': temp_id, 'created_at': now, 'updated_at': now},
    ]
    
    op.bulk_insert(variants_table, variants_data)


def downgrade():
    """Remove seeded data"""
    # Delete in reverse order to respect foreign key constraints
    op.execute("DELETE FROM variants")
    op.execute("DELETE FROM variant_types")
    op.execute("DELETE FROM roles")
