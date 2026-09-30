"""add resume profiles

Revision ID: c64612b7eec7
Revises: 6664a51f0e7a
Create Date: 2026-09-20 11:46:42.240728

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "c64612b7eec7"
down_revision: Union[str, Sequence[str], None] = "6664a51f0e7a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "resume_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            "raw_text",
            sa.Text(),
            nullable=False
        ),
        sa.Column(
            "skills",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=False
        ),
        sa.Column(
            "projects",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=False
        ),
        sa.Column(
            "experience",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=False
        ),
        sa.Column(
            "education",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=False
        ),
        sa.Column(
            "achievements",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=False
        ),
        sa.Column(
            "leadership",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=False
        ),
        sa.Column(
            "certifications",
            postgresql.JSON(astext_type=sa.Text()),
            nullable=False
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"]
        ),
        sa.PrimaryKeyConstraint("id")
    )

    op.create_index(
        "ix_resume_profiles_id",
        "resume_profiles",
        ["id"],
        unique=False
    )

    op.create_index(
        "ix_resume_profiles_user_id",
        "resume_profiles",
        ["user_id"],
        unique=False
    )


def downgrade() -> None:
    op.drop_index(
        "ix_resume_profiles_user_id",
        table_name="resume_profiles"
    )

    op.drop_index(
        "ix_resume_profiles_id",
        table_name="resume_profiles"
    )

    op.drop_table("resume_profiles")
