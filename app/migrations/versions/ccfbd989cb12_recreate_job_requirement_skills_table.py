"""recreate_job_requirement_skills_table

Revision ID: ccfbd989cb12
Revises: 29aa64c67fc9
Create Date: 2025-09-25 06:49:06.570132

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ccfbd989cb12"
down_revision: Union[str, None] = "29aa64c67fc9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Recreate t_job_requirement_skills table for requirement-level skill management."""
    op.create_table(
        "t_job_requirement_skills",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            "job_requirement_id",
            sa.Integer(),
            nullable=False,
            comment="Reference to job requirement",
        ),
        sa.Column(
            "skill_id", sa.Integer(), nullable=False, comment="Reference to skill"
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
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


def downgrade() -> None:
    """Drop t_job_requirement_skills table."""
    op.drop_table("t_job_requirement_skills")
