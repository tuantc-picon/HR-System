"""add_recruitment_count_to_jobs

Revision ID: e649000b6bc6
Revises: c7bcffd33e47
Create Date: 2025-09-28 15:05:41.561713

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e649000b6bc6"
down_revision: Union[str, None] = "c7bcffd33e47"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add recruitment_count column to t_jobs table as nullable first
    op.add_column(
        "t_jobs",
        sa.Column(
            "recruitment_count",
            sa.Integer(),
            nullable=True,
            comment="Number of people to recruit for this position",
        ),
    )

    # Update existing records to have default value of 1
    op.execute(
        "UPDATE t_jobs SET recruitment_count = 1 WHERE recruitment_count IS NULL"
    )

    # Now make the column non-nullable with default
    op.alter_column("t_jobs", "recruitment_count", nullable=False, server_default="1")


def downgrade() -> None:
    """Downgrade schema."""
    # Remove recruitment_count column from t_jobs table
    op.drop_column("t_jobs", "recruitment_count")
