"""seed coffee menu items

Revision ID: 80ead3fe85e5
Revises: cc647bc1aafe
Create Date: 2025-05-22 19:32:18.522492
"""

from datetime import datetime
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = '80ead3fe85e5'
down_revision: Union[str, None] = 'cc647bc1aafe'
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
    coffee_shop_id = '2502896b-ed44-420d-af92-44574740e017'

    # Default variant IDs
    variant_ids = {
        'Small': '96010d54-0ef3-4d37-ac76-f6601a51dc49',
        'No Sugar': 'cc3d70e3-5133-4e94-b2c7-d9a5ba2e8285',
        'Regular Milk': '4bb61b05-6783-42ef-aa2f-1f0e66bc8930',
        'Hot': '1e8db01e-ffba-4c64-9910-6fecd3012b97'
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
