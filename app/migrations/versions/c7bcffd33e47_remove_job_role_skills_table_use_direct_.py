"""remove_job_role_skills_table_use_direct_fk

Revision ID: c7bcffd33e47
Revises: ccfbd989cb12
Create Date: 2025-09-25 08:19:27.025619

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c7bcffd33e47"
down_revision: Union[str, None] = "ccfbd989cb12"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove t_job_role_skills table since m_skills already has job_role_id FK"""
    op.drop_table("t_job_role_skills")


def downgrade() -> None:
    """Recreate t_job_role_skills table if needed"""
    op.create_table(
        "t_job_role_skills",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("job_role_id", sa.Integer(), nullable=False),
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
            ["job_role_id"],
            ["m_job_roles.id"],
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"],
            ["m_skills.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
