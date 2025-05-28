"""seed_coffee_menu_items

Revision ID: 460c252a14fb
Revises: 40d2709024b8
Create Date: 2025-05-23 17:37:09.395981

"""
from datetime import datetime
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision: str = '460c252a14fb'
down_revision: Union[str, None] = '40d2709024b8'
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
    coffee_shop_id = 'b7b58e4f-7bd8-4ae3-94a2-925e53835723'

    # Default variant IDs
    variant_ids = {
        'Small': '7035e3a0-998f-4fc1-b7ef-9d62da3e5fff',
        'No Sugar': 'ccc73923-212b-4b48-9b21-457e8ee8998c',
        'Regular Milk': 'b984ffc0-f0d1-4947-acae-87ad6c0c0ff7',
        'Hot': '006296e2-ca65-4626-9985-517bf9861526'
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


