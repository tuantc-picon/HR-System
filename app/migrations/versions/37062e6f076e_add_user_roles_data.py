"""add_user_roles_data

Revision ID: 37062e6f076e
Revises: 73567935c8df
Create Date: 2025-09-16 13:50:11.899199

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '37062e6f076e'
down_revision: Union[str, None] = '73567935c8df'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema and populate user roles."""
    import csv
    import os
    from datetime import datetime
    from sqlalchemy import text

    # Get database connection
    connection = op.get_bind()

    # Get the path to CSV files
    migrations_dir = os.path.dirname(os.path.dirname(__file__))
    csv_dir = os.path.join(migrations_dir, 'master_data')
    csv_path = os.path.join(csv_dir, 'user_roles.csv')

    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Check if user role already exists
                result = connection.execute(
                    text("SELECT id FROM m_roles WHERE name = :name"),
                    {"name": row['name'].strip()}
                ).fetchone()

                if not result:
                    connection.execute(
                        text("""
                            INSERT INTO m_roles (name, description, is_active, created_at)
                            VALUES (:name, :description, :is_active, :created_at)
                        """),
                        {
                            "name": row['name'].strip(),
                            "description": row['description'].strip(),
                            "is_active": True,
                            "created_at": datetime.utcnow()
                        }
                    )


def downgrade() -> None:
    """Downgrade schema - remove user roles data."""
    from sqlalchemy import text

    connection = op.get_bind()
    connection.execute(text("DELETE FROM m_roles WHERE name IN ('Admin', 'HR Manager', 'Recruiter', 'Interviewer', 'Employee')"))
