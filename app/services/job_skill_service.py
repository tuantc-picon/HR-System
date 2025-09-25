from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from model.job.job_skills import JobSkill
from model.master.skills import Skill
from model.master.job_roles import JobRole
from model.job.job_role_skills import JobRoleSkill
from services.base_service import BaseService
from core.common.exceptions import HRSystemBaseException
from starlette import status


class JobSkillService(BaseService[JobSkill]):
    """Service for managing job-skill associations (job-level skill selection)"""

    def __init__(self):
        super().__init__(JobSkill)

    def add_skill_to_job(self, db: Session, job_id: int, skill_id: int) -> JobSkill:
        """Add a skill to a job"""
        # Check if association already exists
        existing = (
            db.query(JobSkill)
            .filter(
                and_(
                    JobSkill.job_id == job_id,
                    JobSkill.skill_id == skill_id,
                    JobSkill.deleted_at.is_(None),
                )
            )
            .first()
        )

        if existing:
            raise HRSystemBaseException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Skill is already associated with this job",
            )

        # Create new association
        job_skill = JobSkill(job_id=job_id, skill_id=skill_id)
        db.add(job_skill)
        db.commit()
        db.refresh(job_skill)
        return job_skill

    def remove_skill_from_job(self, db: Session, job_id: int, skill_id: int) -> bool:
        """Remove a skill from a job"""
        job_skill = (
            db.query(JobSkill)
            .filter(
                and_(
                    JobSkill.job_id == job_id,
                    JobSkill.skill_id == skill_id,
                    JobSkill.deleted_at.is_(None),
                )
            )
            .first()
        )

        if not job_skill:
            return False

        return self.soft_delete(db, job_skill.id)

    def get_skills_for_job(self, db: Session, job_id: int) -> List[Skill]:
        """Get all skills associated with a job"""
        # Get all skill associations for the job
        associations = (
            db.query(JobSkill)
            .filter(
                and_(
                    JobSkill.job_id == job_id,
                    JobSkill.deleted_at.is_(None),
                )
            )
            .all()
        )

        if not associations:
            return []

        # Get the skills
        skill_ids = [assoc.skill_id for assoc in associations]
        return (
            db.query(Skill)
            .filter(
                and_(
                    Skill.id.in_(skill_ids),
                    Skill.is_active == True,
                    Skill.deleted_at.is_(None),
                )
            )
            .all()
        )

    def get_available_skills_for_job_role(
        self, db: Session, job_role_id: int
    ) -> List[Skill]:
        """Get all skills available for a job role (for skill selection)"""
        # Get all skill associations for the job role
        associations = (
            db.query(JobRoleSkill)
            .filter(
                and_(
                    JobRoleSkill.job_role_id == job_role_id,
                    JobRoleSkill.deleted_at.is_(None),
                )
            )
            .all()
        )

        if not associations:
            return []

        # Get the skills
        skill_ids = [assoc.skill_id for assoc in associations]
        return (
            db.query(Skill)
            .filter(
                and_(
                    Skill.id.in_(skill_ids),
                    Skill.is_active == True,
                    Skill.deleted_at.is_(None),
                )
            )
            .all()
        )

    def bulk_add_skills_to_job(
        self, db: Session, job_id: int, skill_ids: List[int]
    ) -> List[JobSkill]:
        """Add multiple skills to a job"""
        # Remove existing skills first
        db.query(JobSkill).filter(JobSkill.job_id == job_id).delete()

        # Add new skills
        job_skills = []
        for skill_id in skill_ids:
            job_skill = JobSkill(job_id=job_id, skill_id=skill_id)
            db.add(job_skill)
            job_skills.append(job_skill)

        db.commit()

        # Refresh all objects
        for job_skill in job_skills:
            db.refresh(job_skill)

        return job_skills

    def bulk_remove_skills_from_job(
        self, db: Session, job_id: int, skill_ids: List[int]
    ) -> int:
        """Remove multiple skills from a job"""
        deleted_count = 0
        for skill_id in skill_ids:
            if self.remove_skill_from_job(db, job_id, skill_id):
                deleted_count += 1
        return deleted_count

    def validate_skills_for_job_role(
        self, db: Session, job_role_id: int, skill_ids: List[int]
    ) -> bool:
        """Validate that all provided skills belong to the job role"""
        available_skill_ids = [
            assoc.skill_id
            for assoc in db.query(JobRoleSkill)
            .filter(
                and_(
                    JobRoleSkill.job_role_id == job_role_id,
                    JobRoleSkill.deleted_at.is_(None),
                )
            )
            .all()
        ]

        return all(skill_id in available_skill_ids for skill_id in skill_ids)

    def count_skills_for_job(self, db: Session, job_id: int) -> int:
        """Count the number of skills associated with a job"""
        return (
            db.query(JobSkill)
            .filter(
                and_(
                    JobSkill.job_id == job_id,
                    JobSkill.deleted_at.is_(None),
                )
            )
            .count()
        )


# Create singleton instance
job_skill_service = JobSkillService()
