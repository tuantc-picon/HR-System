"""populate_master_data_from_csv

Revision ID: 73567935c8df
Revises: c2c8c6fe2941
Create Date: 2025-09-16 13:47:33.343004

"""
from typing import Sequence, Union
import csv
import os
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '73567935c8df'
down_revision: Union[str, None] = 'c2c8c6fe2941'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema and populate master data from CSV files."""
    # Get database connection
    connection = op.get_bind()

    # Get the path to CSV files
    migrations_dir = os.path.dirname(os.path.dirname(__file__))
    csv_dir = os.path.join(migrations_dir, 'master_data')

    # Populate job roles first (since skills depend on them)
    populate_job_roles(connection, csv_dir)

    # Populate skills (depends on job roles)
    populate_skills(connection, csv_dir)

    # Populate certificates
    populate_certificates(connection, csv_dir)

    # Populate user roles
    populate_user_roles(connection, csv_dir)


def populate_job_roles(connection, csv_dir):
    """Populate job roles from CSV"""
    csv_path = os.path.join(csv_dir, 'job_roles.csv')
    if not os.path.exists(csv_path):
        return

    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Check if job role already exists
            result = connection.execute(
                text("SELECT id FROM m_job_roles WHERE name = :name"),
                {"name": row['name'].strip()}
            ).fetchone()

            if not result:
                connection.execute(
                    text("""
                        INSERT INTO m_job_roles (name, description, is_active, created_at)
                        VALUES (:name, :description, :is_active, :created_at)
                    """),
                    {
                        "name": row['name'].strip(),
                        "description": row['description'].strip(),
                        "is_active": True,
                        "created_at": datetime.utcnow()
                    }
                )


def populate_skills(connection, csv_dir):
    """Populate skills from CSV"""
    csv_path = os.path.join(csv_dir, 'skills.csv')
    if not os.path.exists(csv_path):
        return

    # Get job roles mapping
    job_roles_result = connection.execute(text("SELECT id, name FROM m_job_roles")).fetchall()
    job_role_map = {row[1]: row[0] for row in job_roles_result}

    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            job_role_name = row['job_role_name'].strip()
            job_role_id = job_role_map.get(job_role_name)

            if job_role_id:
                # Check if skill already exists for this job role
                result = connection.execute(
                    text("SELECT id FROM m_skills WHERE name = :name AND job_role_id = :job_role_id"),
                    {"name": row['name'].strip(), "job_role_id": job_role_id}
                ).fetchone()

                if not result:
                    connection.execute(
                        text("""
                            INSERT INTO m_skills (job_role_id, name, description, is_active, created_at)
                            VALUES (:job_role_id, :name, :description, :is_active, :created_at)
                        """),
                        {
                            "job_role_id": job_role_id,
                            "name": row['name'].strip(),
                            "description": f"Skill for {job_role_name}",
                            "is_active": True,
                            "created_at": datetime.utcnow()
                        }
                    )


def populate_certificates(connection, csv_dir):
    """Populate certificates from CSV"""
    csv_path = os.path.join(csv_dir, 'certificates.csv')
    if not os.path.exists(csv_path):
        return

    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            # Check if certificate already exists
            result = connection.execute(
                text("SELECT id FROM m_certificates WHERE name = :name"),
                {"name": row['name'].strip()}
            ).fetchone()

            if not result:
                connection.execute(
                    text("""
                        INSERT INTO m_certificates (name, description, category, is_active, created_at)
                        VALUES (:name, :description, :category, :is_active, :created_at)
                    """),
                    {
                        "name": row['name'].strip(),
                        "description": row['description'].strip(),
                        "category": int(row['category']),
                        "is_active": True,
                        "created_at": datetime.utcnow()
                    }
                )


def populate_user_roles(connection, csv_dir):
    """Populate user roles from CSV"""
    csv_path = os.path.join(csv_dir, 'user_roles.csv')
    if not os.path.exists(csv_path):
        return

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
    """Downgrade schema - remove populated master data."""
    connection = op.get_bind()

    # Delete in reverse dependency order
    connection.execute(text("DELETE FROM m_skills"))
    connection.execute(text("DELETE FROM m_certificates"))
    connection.execute(text("DELETE FROM m_roles"))
    connection.execute(text("DELETE FROM m_job_roles"))
