"""add_reset_pass_column

Revision ID: 659cee522805
Revises: 9789c39bbe0d
Create Date: 2025-05-29 00:50:52.304245

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '659cee522805'
down_revision: Union[str, None] = '9789c39bbe0d'
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

