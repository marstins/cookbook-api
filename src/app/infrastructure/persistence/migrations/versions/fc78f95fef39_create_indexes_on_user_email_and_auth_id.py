"""create indexes on user email and auth_id

Revision ID: fc78f95fef39
Revises: 29d45d5e2064
Create Date: 2026-10-19 10:45:49.039528

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'fc78f95fef39'
down_revision: Union[str, Sequence[str], None] = '29d45d5e2064'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('users') as batch_op:
        batch_op.create_unique_constraint('uq_auth_id', ['auth_id'])
        batch_op.create_index('ik_users_auth_id', ['auth_id'])
        batch_op.create_index('ik_users_email', ['email'])


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_constraint('uq_auth_id')
        batch_op.drop_index('ik_users_auth_id')
        batch_op.drop_index('ik_users_email')

