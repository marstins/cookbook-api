"""removes nullable from tags columns in recipe

Revision ID: 6bbe0c9a7a22
Revises: 0267f89bd0b1
Create Date: 2026-10-10 16:51:31.081764

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6bbe0c9a7a22'
down_revision: Union[str, Sequence[str], None] = '0267f89bd0b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("UPDATE recipes SET tags = '[]' WHERE tags IS NULL")
    with op.batch_alter_table('recipes') as batch_op:
        batch_op.alter_column('tags', existing_type=sa.TEXT(), nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('recipes') as batch_op:
        batch_op.alter_column('tags', existing_type=sa.TEXT(), nullable=True)
