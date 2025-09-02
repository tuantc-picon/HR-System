from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from model.job.job_requirements import JobRequirement
from services.base_service import BaseService
from schema.request.job_requirement_schemas import JobRequirementCreateRequest, JobRequirementUpdateRequest
from core.common.exceptions import HRSystemBaseException
from starlette import status


class JobRequirementService(BaseService[JobRequirement]):
    def __init__(self):
        super().__init__(JobRequirement)

    def create_job_requirement(self, db: Session, job_requirement_data: JobRequirementCreateRequest) -> JobRequirement:
        """Create a new job requirement with validation"""
        # Validate salary range
        if (job_requirement_data.min_salary is not None and 
            job_requirement_data.max_salary is not None and 
            job_requirement_data.min_salary > job_requirement_data.max_salary):
            raise HRSystemBaseException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Minimum salary cannot be greater than maximum salary"
            )
        
        # Validate experience range
        if (job_requirement_data.min_experience is not None and 
            job_requirement_data.max_experience is not None and 
            job_requirement_data.min_experience > job_requirement_data.max_experience):
            raise HRSystemBaseException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Minimum experience cannot be greater than maximum experience"
            )
        
        job_requirement_dict = job_requirement_data.model_dump()
        return self.create(db, job_requirement_dict)

    def update_job_requirement(self, db: Session, job_requirement_id: int, job_requirement_data: JobRequirementUpdateRequest) -> Optional[JobRequirement]:
        """Update job requirement with validation"""
        # Get existing record for validation
        existing_requirement = self.get_by_id(db, job_requirement_id)
        if not existing_requirement:
            return None
        
        # Prepare updated values for validation
        min_salary = job_requirement_data.min_salary if job_requirement_data.min_salary is not None else existing_requirement.min_salary
        max_salary = job_requirement_data.max_salary if job_requirement_data.max_salary is not None else existing_requirement.max_salary
        min_experience = job_requirement_data.min_experience if job_requirement_data.min_experience is not None else existing_requirement.min_experience
        max_experience = job_requirement_data.max_experience if job_requirement_data.max_experience is not None else existing_requirement.max_experience
        
        # Validate salary range
        if min_salary is not None and max_salary is not None and min_salary > max_salary:
            raise HRSystemBaseException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Minimum salary cannot be greater than maximum salary"
            )
        
        # Validate experience range
        if min_experience is not None and max_experience is not None and min_experience > max_experience:
            raise HRSystemBaseException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Minimum experience cannot be greater than maximum experience"
            )
        
        job_requirement_dict = job_requirement_data.model_dump(exclude_unset=True)
        return self.update(db, job_requirement_id, job_requirement_dict)

    def get_requirements_by_job(self, db: Session, job_id: int) -> List[JobRequirement]:
        """Get all requirements for a specific job"""
        return db.query(JobRequirement).filter(
            and_(
                JobRequirement.job_id == job_id,
                JobRequirement.deleted_at.is_(None)
            )
        ).all()


# Create singleton instance
job_requirement_service = JobRequirementService()
