from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from model.job.job_requirements import JobRequirement
from model.job.job_requirement_skills import JobRequirementSkill
from model.master.job_roles import JobRole
from model.master.skills import Skill
from services.base_service import BaseService
from schema.request.job_requirement_schemas import (
    JobRequirementCreateRequest,
    JobRequirementUpdateRequest,
)
from core.common.exceptions import HRSystemBaseException
from starlette import status


class JobRequirementService(BaseService[JobRequirement]):
    def __init__(self):
        super().__init__(JobRequirement)

    def create_job_requirement(
        self, db: Session, job_requirement_data: JobRequirementCreateRequest
    ) -> JobRequirement:
        """Create a new job requirement with validation"""
        try:
            # Validate job_role_id if provided
            if job_requirement_data.job_role_id:
                job_role = (
                    db.query(JobRole)
                    .filter(JobRole.id == job_requirement_data.job_role_id)
                    .first()
                )
                if not job_role:
                    raise HRSystemBaseException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="Job role not found",
                    )
                if not job_role.is_active:
                    raise HRSystemBaseException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="Job role is not active",
                    )

            # Validate skill IDs if provided
            if job_requirement_data.skill_ids:
                skills = (
                    db.query(Skill)
                    .filter(Skill.id.in_(job_requirement_data.skill_ids))
                    .all()
                )
                if len(skills) != len(job_requirement_data.skill_ids):
                    raise HRSystemBaseException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="One or more skills not found",
                    )

            # Validate salary range
            if (
                job_requirement_data.min_salary is not None
                and job_requirement_data.max_salary is not None
                and job_requirement_data.min_salary > job_requirement_data.max_salary
            ):
                raise HRSystemBaseException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Minimum salary cannot be greater than maximum salary",
                )

            # Validate experience range
            if (
                job_requirement_data.min_experience is not None
                and job_requirement_data.max_experience is not None
                and job_requirement_data.min_experience
                > job_requirement_data.max_experience
            ):
                raise HRSystemBaseException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Minimum experience cannot be greater than maximum experience",
                )

            # Create job requirement
            job_requirement_dict = job_requirement_data.model_dump(
                exclude={"skill_ids"}
            )
            job_requirement = self.create(db, job_requirement_dict)

            # Create skill associations if provided
            if job_requirement_data.skill_ids:
                for skill_id in job_requirement_data.skill_ids:
                    skill_assoc = JobRequirementSkill(
                        job_requirement_id=job_requirement.id, skill_id=skill_id
                    )
                    db.add(skill_assoc)

            db.commit()
            return job_requirement

        except Exception as e:
            db.rollback()
            if isinstance(e, HRSystemBaseException):
                raise e
            raise HRSystemBaseException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to create job requirement: {str(e)}",
            )

    def update_job_requirement(
        self,
        db: Session,
        job_requirement_id: int,
        job_requirement_data: JobRequirementUpdateRequest,
    ) -> Optional[JobRequirement]:
        """Update job requirement with validation"""
        try:
            # Get existing record for validation
            existing_requirement = self.get_by_id(db, job_requirement_id)
            if not existing_requirement:
                return None

            # Validate job_role_id if provided
            if job_requirement_data.job_role_id:
                job_role = (
                    db.query(JobRole)
                    .filter(JobRole.id == job_requirement_data.job_role_id)
                    .first()
                )
                if not job_role:
                    raise HRSystemBaseException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="Job role not found",
                    )
                if not job_role.is_active:
                    raise HRSystemBaseException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        message="Job role is not active",
                    )

            # Validate skill IDs if provided
            if job_requirement_data.skill_ids is not None:
                if job_requirement_data.skill_ids:
                    skills = (
                        db.query(Skill)
                        .filter(Skill.id.in_(job_requirement_data.skill_ids))
                        .all()
                    )
                    if len(skills) != len(job_requirement_data.skill_ids):
                        raise HRSystemBaseException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            message="One or more skills not found",
                        )

            # Prepare updated values for validation
            min_salary = (
                job_requirement_data.min_salary
                if job_requirement_data.min_salary is not None
                else existing_requirement.min_salary
            )
            max_salary = (
                job_requirement_data.max_salary
                if job_requirement_data.max_salary is not None
                else existing_requirement.max_salary
            )
            min_experience = (
                job_requirement_data.min_experience
                if job_requirement_data.min_experience is not None
                else existing_requirement.min_experience
            )
            max_experience = (
                job_requirement_data.max_experience
                if job_requirement_data.max_experience is not None
                else existing_requirement.max_experience
            )

            # Validate salary range
            if (
                min_salary is not None
                and max_salary is not None
                and min_salary > max_salary
            ):
                raise HRSystemBaseException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Minimum salary cannot be greater than maximum salary",
                )

            # Validate experience range
            if (
                min_experience is not None
                and max_experience is not None
                and min_experience > max_experience
            ):
                raise HRSystemBaseException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Minimum experience cannot be greater than maximum experience",
                )

            # Update job requirement skills if provided
            if job_requirement_data.skill_ids is not None:
                # Delete existing skill associations
                db.query(JobRequirementSkill).filter(
                    JobRequirementSkill.job_requirement_id == job_requirement_id
                ).delete()

                # Create new skill associations
                for skill_id in job_requirement_data.skill_ids:
                    skill_assoc = JobRequirementSkill(
                        job_requirement_id=job_requirement_id, skill_id=skill_id
                    )
                    db.add(skill_assoc)

            # Update job requirement
            job_requirement_dict = job_requirement_data.model_dump(
                exclude_unset=True, exclude={"skill_ids"}
            )
            updated_requirement = self.update(
                db, job_requirement_id, job_requirement_dict
            )

            db.commit()
            return updated_requirement

        except Exception as e:
            db.rollback()
            if isinstance(e, HRSystemBaseException):
                raise e
            raise HRSystemBaseException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=f"Failed to update job requirement: {str(e)}",
            )

    def get_requirements_by_job(self, db: Session, job_id: int) -> List[JobRequirement]:
        """Get all requirements for a specific job"""
        return (
            db.query(JobRequirement)
            .filter(
                and_(
                    JobRequirement.job_id == job_id, JobRequirement.deleted_at.is_(None)
                )
            )
            .all()
        )


# Create singleton instance
job_requirement_service = JobRequirementService()
