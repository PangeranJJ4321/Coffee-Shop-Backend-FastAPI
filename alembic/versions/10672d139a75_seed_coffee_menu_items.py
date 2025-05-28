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
    coffee_shop_id = '8dede67b-7f3c-4c30-9a05-544f8f093bd5'

    # Default variant IDs
    variant_ids = {
        'Small': '8bb51852-76cf-4ce4-9acf-c38bc34aa392',
        'No Sugar': '6343f654-1232-47bc-9930-cad97f37c02f',
        'Regular Milk': '8eee9366-cf80-4aee-9f85-dc030955622a',
        'Hot': '10ead29f-6c56-4e14-8773-bd091daa5389'
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



