"""seed_coffee_menu_items

Revision ID: 10672d139a75
Revises: 67a53224a564
Create Date: 2025-05-29 01:04:35.480149

"""
from datetime import datetime
from typing import Sequence, Union
import uuid

from alembic import op 
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '10672d139a75'
down_revision: Union[str, None] = '67a53224a564'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Define table references
menu_items_table = table(
    'coffee_menu',
    column('id', UUID),
    column('name', sa.String),
    column('price', sa.Integer),
    column('description', sa.Text),
    column('coffee_shop_id', UUID),
    column('is_available', sa.Boolean),
    column('created_at', sa.DateTime),
    column('updated_at', sa.DateTime),
)

coffee_variants_table = table(
    'coffee_variants',
    column('id', UUID),
    column('coffee_id', UUID),
    column('variant_id', UUID),
    column('is_default', sa.Boolean),
    column('created_at', sa.DateTime),
    column('updated_at', sa.DateTime),
)

def upgrade():
    now = datetime.utcnow()
    coffee_shop_id = 'ed634a6f-c12d-4ed4-8975-1926a2ee4a43'

    # Default variant IDs
    variant_ids = {
        'Small': '6318fdae-4ae7-403c-a978-40bf550b7f0c',
        'No Sugar': '20b2b4de-2ff4-485e-8de3-1de47baccdfa',
        'Regular Milk': '805d683f-6da1-4b16-b960-4c83b50438a0',
        'Hot': '6efc7366-4924-4786-bb39-02b62627ac07'
    }

    menus = [
        {"name": "Cappuccino", "price": 35000, "description": "Coffee with steamed milk foam"},
        {"name": "Latte", "price": 32000, "description": "Smooth milk coffee"},
        {"name": "Espresso", "price": 22000, "description": "Strong and bold coffee shot"},
        {"name": "Mocha", "price": 38000, "description": "Chocolate flavored coffee"},
        {"name": "Flat White", "price": 34000, "description": "Smooth espresso with milk"},
    ]

    menu_items_data = []
    coffee_variants_data = []

    for menu in menus:
        coffee_id = str(uuid.uuid4())
        menu_items_data.append({
            'id': coffee_id,
            'name': menu['name'],
            'price': menu['price'],
            'description': menu['description'],
            'coffee_shop_id': coffee_shop_id,
            'is_available': True,
            'created_at': now,
            'updated_at': now
        })

        for variant_name, variant_id in variant_ids.items():
            coffee_variants_data.append({
                'id': str(uuid.uuid4()),
                'coffee_id': coffee_id,
                'variant_id': variant_id,
                'is_default': True,
                'created_at': now,
                'updated_at': now
            })

    op.bulk_insert(menu_items_table, menu_items_data)
    op.bulk_insert(coffee_variants_table, coffee_variants_data)


def downgrade():
    menu_names = ("Cappuccino", "Latte", "Espresso", "Mocha", "Flat White")
    name_tuple = "(" + ", ".join([f"'{name}'" for name in menu_names]) + ")"

    op.execute(f"""
        DELETE FROM coffee_variants
        WHERE coffee_id IN (
            SELECT id FROM coffee_menu WHERE name IN {name_tuple}
        )
    """)
    op.execute(f"DELETE FROM coffee_menu WHERE name IN {name_tuple}")



