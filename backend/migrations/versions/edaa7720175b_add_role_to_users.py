"""add role to users

Revision ID: edaa7720175b
Revises: 6e16a286d4b9
Create Date: 2026-10-04 08:41:25.641544

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'edaa7720175b'
down_revision: Union[str, None] = '6e16a286d4b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # server_default backfills existing rows, so every current user becomes a citizen
    op.add_column(
        'users',
        sa.Column('role', sa.String(length=20), nullable=False, server_default='citizen'),
    )


def downgrade() -> None:
    op.drop_column('users', 'role')
