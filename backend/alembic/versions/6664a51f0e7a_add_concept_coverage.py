"""add concept coverage

Revision ID: 6664a51f0e7a
Revises:
Create Date: 2026-09-19 16:05:25.858638

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6664a51f0e7a'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'evaluations',
        sa.Column('concept_coverage', sa.Float(), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column(
        'evaluations',
        'concept_coverage'
    )
