import csv
import os
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from model.master.job_roles import JobRole
from model.master.skills import Skill
from model.master.certificates import Certificate
from model.master.user_roles import UserRole
from core.common.exceptions import HRSystemBaseException
from core.enum.master import MasterDataTypeEnum
from starlette import status


class MasterDataService:
    def __init__(self):
        # Get the correct path to migrations/master_data directory
        # __file__ is in app/services/, so we need to go up to app/ then to migrations/master_data/
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "migrations", "master_data"
        )

    def populate_from_csv(self, db: Session) -> Dict[str, int]:
        """Populate master data from CSV files"""
        results = {"job_roles": 0, "skills": 0, "certificates": 0, "user_roles": 0}

        try:
            # Clear existing data first
            self._clear_existing_data(db)

            # Populate job roles first (since skills depend on them)
            results["job_roles"] = self._populate_job_roles(db)

            # Populate skills (depends on job roles)
            results["skills"] = self._populate_skills(db)

            # Populate certificates
            results["certificates"] = self._populate_certificates(db)

            # Populate user roles
            results["user_roles"] = self._populate_user_roles(db)

            db.commit()
            return results

        except Exception as e:
            db.rollback()
            raise HRSystemBaseException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to populate master data: {str(e)}",
            )

    def _clear_existing_data(self, db: Session):
        """Clear existing master data"""
        # Delete in reverse dependency order, handling foreign key constraints
        # First, set job_role_id to NULL in jobs table
        from model.job.jobs import Job
        from model.job.job_skills import JobSkill
        from model.job.job_requirement_certificates import JobRequirementCertificate
        from model.job.job_requirement_black_lists import JobRequirementBlackList
        from model.job.job_requirements import JobRequirement

        db.query(Job).update({Job.job_role_id: None})

        # Delete job requirement associations first
        db.query(JobRequirementCertificate).delete()
        db.query(JobRequirementBlackList).delete()
        db.query(JobRequirement).delete()

        # Delete job_skills associations (they reference skills)
        db.query(JobSkill).delete()

        # Delete skills (they reference job_roles)
        db.query(Skill).delete()

        # Delete certificates
        db.query(Certificate).delete()

        # Delete user roles
        db.query(UserRole).delete()

        # Finally delete job roles
        db.query(JobRole).delete()

    def _populate_job_roles(self, db: Session) -> int:
        """Populate job roles from CSV"""
        csv_path = os.path.join(self.data_dir, "job_roles.csv")
        if not os.path.exists(csv_path):
            return 0

        count = 0
        with open(csv_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                job_role = JobRole(
                    name=row["name"].strip(),
                    description=row["description"].strip(),
                    is_active=True,
                )
                db.add(job_role)
                count += 1

        db.flush()  # Flush to get IDs
        return count

    def _populate_skills(self, db: Session) -> int:
        """Populate skills from CSV"""
        csv_path = os.path.join(self.data_dir, "skills.csv")
        if not os.path.exists(csv_path):
            return 0

        # Get job roles mapping
        job_roles = db.query(JobRole).all()
        job_role_map = {role.name: role.id for role in job_roles}

        count = 0
        with open(csv_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                job_role_name = row["job_role_name"].strip()
                job_role_id = job_role_map.get(job_role_name)

                if job_role_id:
                    skill = Skill(
                        job_role_id=job_role_id,
                        name=row["name"].strip(),
                        description=f"Skill for {job_role_name}",
                        is_active=True,
                    )
                    db.add(skill)
                    count += 1

        db.flush()
        return count

    def _populate_certificates(self, db: Session) -> int:
        """Populate certificates from CSV"""
        csv_path = os.path.join(self.data_dir, "certificates.csv")
        if not os.path.exists(csv_path):
            return 0

        count = 0
        with open(csv_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                certificate = Certificate(
                    name=row["name"].strip(),
                    description=row["description"].strip(),
                    category=int(row["category"]),
                    is_active=True,
                )
                db.add(certificate)
                count += 1

        db.flush()
        return count

    def _populate_user_roles(self, db: Session) -> int:
        """Populate user roles from CSV"""
        csv_path = os.path.join(self.data_dir, "user_roles.csv")
        if not os.path.exists(csv_path):
            return 0

        count = 0
        with open(csv_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                user_role = UserRole(
                    name=row["name"].strip(),
                    description=row["description"].strip(),
                    is_active=True,
                )
                db.add(user_role)
                count += 1

        db.flush()
        return count

    def get_all_master_data(self, db: Session) -> Dict[str, List[Any]]:
        """Get all master data as lists (excluding black_list as requested)"""
        return {
            "job_roles": db.query(JobRole)
            .filter(and_(JobRole.is_active == True, JobRole.deleted_at.is_(None)))
            .all(),
            "skills": db.query(Skill)
            .filter(and_(Skill.is_active == True, Skill.deleted_at.is_(None)))
            .all(),
            "certificates": db.query(Certificate)
            .filter(
                and_(Certificate.is_active == True, Certificate.deleted_at.is_(None))
            )
            .all(),
            "user_roles": db.query(UserRole)
            .filter(and_(UserRole.is_active == True, UserRole.deleted_at.is_(None)))
            .all(),
        }

    def get_master_data_by_type(
        self, db: Session, data_type: MasterDataTypeEnum
    ) -> List[Any]:
        """Get specific master data by type"""
        try:
            if data_type == MasterDataTypeEnum.CERTIFICATES:
                return (
                    db.query(Certificate)
                    .filter(
                        and_(
                            Certificate.is_active == True,
                            Certificate.deleted_at.is_(None),
                        )
                    )
                    .all()
                )
            elif data_type == MasterDataTypeEnum.JOB_ROLES:
                return (
                    db.query(JobRole)
                    .filter(
                        and_(JobRole.is_active == True, JobRole.deleted_at.is_(None))
                    )
                    .all()
                )
            elif data_type == MasterDataTypeEnum.SKILLS:
                return (
                    db.query(Skill)
                    .filter(and_(Skill.is_active == True, Skill.deleted_at.is_(None)))
                    .all()
                )
            elif data_type == MasterDataTypeEnum.USER_ROLES:
                return (
                    db.query(UserRole)
                    .filter(
                        and_(UserRole.is_active == True, UserRole.deleted_at.is_(None))
                    )
                    .all()
                )
            else:
                raise HRSystemBaseException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message=f"Invalid master data type: {data_type}",
                )
        except Exception as e:
            if isinstance(e, HRSystemBaseException):
                raise e
            raise HRSystemBaseException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to retrieve {data_type} data: {str(e)}",
            )


# Create singleton instance
master_data_service = MasterDataService()
