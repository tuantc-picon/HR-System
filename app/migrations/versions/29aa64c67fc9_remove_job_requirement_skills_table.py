"""remove_job_requirement_skills_table

Revision ID: 29aa64c67fc9
Revises: 6e3fb122d042
Create Date: 2025-09-24 21:02:17.801640

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "29aa64c67fc9"
down_revision: Union[str, None] = "6e3fb122d042"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Drop the t_job_requirement_skills table as it represents an incorrect relationship
    # Skills should be associated with job roles, not individual job requirements
    op.drop_table("t_job_requirement_skills")


def downgrade() -> None:
    """Downgrade schema."""
    # Recreate the t_job_requirement_skills table if needed for rollback
    op.create_table(
        "t_job_requirement_skills",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_requirement_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["job_requirement_id"],
            ["t_job_requirements.id"],
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"],
            ["m_skills.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
