from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from model.master.job_roles import JobRole
from model.master.skills import Skill

# JobRoleSkill removed - using direct FK in m_skills table
from services.base_service import BaseService
from schema.request.job_role_schemas import JobRoleCreateRequest, JobRoleUpdateRequest
from core.common.exceptions import HRSystemBaseException
from starlette import status


class JobRoleService(BaseService[JobRole]):
    def __init__(self):
        super().__init__(JobRole)

    def create_job_role(
        self, db: Session, job_role_data: JobRoleCreateRequest
    ) -> JobRole:
        """Create a new job role with validation"""
        # Check if job role name already exists
        existing_job_role = self.get_by_field(db, "name", job_role_data.name)
        if existing_job_role:
            raise HRSystemBaseException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Job role name already exists",
            )

        job_role_dict = job_role_data.model_dump()
        return self.create(db, job_role_dict)

    def update_job_role(
        self, db: Session, job_role_id: int, job_role_data: JobRoleUpdateRequest
    ) -> Optional[JobRole]:
        """Update job role with validation"""
        # If name is being updated, check for duplicates
        if job_role_data.name:
            existing_job_role = self.get_by_field(db, "name", job_role_data.name)
            if existing_job_role and existing_job_role.id != job_role_id:
                raise HRSystemBaseException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Job role name already exists",
                )

        job_role_dict = job_role_data.model_dump(exclude_unset=True)
        return self.update(db, job_role_id, job_role_dict)

    def get_active_job_roles(self, db: Session) -> List[JobRole]:
        """Get all active job roles"""
        return (
            db.query(JobRole)
            .filter(and_(JobRole.is_active == True, JobRole.deleted_at.is_(None)))
            .all()
        )

    def activate_job_role(self, db: Session, job_role_id: int) -> Optional[JobRole]:
        """Activate a job role"""
        job_role = self.get_by_id(db, job_role_id)
        if not job_role:
            return None

        job_role.is_active = True
        db.commit()
        db.refresh(job_role)
        return job_role

    def deactivate_job_role(self, db: Session, job_role_id: int) -> Optional[JobRole]:
        """Deactivate a job role"""
        job_role = self.get_by_id(db, job_role_id)
        if not job_role:
            return None

        job_role.is_active = False
        db.commit()
        db.refresh(job_role)
        return job_role

    def search_job_roles_by_name(self, db: Session, name: str) -> List[JobRole]:
        """Search job roles by name (case-insensitive)"""
        return (
            db.query(JobRole)
            .filter(and_(JobRole.name.ilike(f"%{name}%"), JobRole.deleted_at.is_(None)))
            .all()
        )

    def get_skills_for_job_role(self, db: Session, job_role_id: int) -> List[Skill]:
        """Get all skills associated with a job role using direct FK"""
        return (
            db.query(Skill)
            .filter(
                and_(
                    Skill.job_role_id == job_role_id,
                    Skill.is_active == True,
                    Skill.deleted_at.is_(None),
                )
            )
            .all()
        )

    def get_job_role_with_skills(self, db: Session, job_role_id: int) -> Optional[dict]:
        """Get a job role with its associated skills"""
        job_role = self.get_by_id(db, job_role_id)
        if not job_role:
            return None

        skills = self.get_skills_for_job_role(db, job_role_id)
        return {"job_role": job_role, "skills": skills}

    def count_skills_for_job_role(self, db: Session, job_role_id: int) -> int:
        """Count the number of skills associated with a job role"""
        return (
            db.query(JobRoleSkill)
            .filter(
                and_(
                    JobRoleSkill.job_role_id == job_role_id,
                    JobRoleSkill.deleted_at.is_(None),
                )
            )
            .count()
        )


# Create singleton instance
job_role_service = JobRoleService()
