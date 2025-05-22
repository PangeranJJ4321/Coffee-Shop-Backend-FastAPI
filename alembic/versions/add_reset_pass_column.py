"""Add password reset columns to users table

Revision ID: add_password_reset_columns
Revises: [previous_revision_id]
Create Date: 2024-12-20 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_password_reset_columns'
down_revision: Union[str, None] = "seed_001"  # Replace with your previous revision ID
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add password reset columns to users table"""
    # Add reset_token column
    op.add_column('users', sa.Column('reset_token', sa.String(), nullable=True))
    
    # Add reset_token_expires column
    op.add_column('users', sa.Column('reset_token_expires', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Remove password reset columns from users table"""
    # Drop reset_token_expires column
    op.drop_column('users', 'reset_token_expires')
    
    # Drop reset_token column
    op.drop_column('users', 'reset_token')