from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from model.job.job_requirement_black_lists import JobRequirementBlackList
from services.base_service import BaseService
from schema.request.job_requirement_black_list_schemas import (
    JobRequirementBlackListCreateRequest,
    JobRequirementBlackListUpdateRequest,
)
from core.common.exceptions import HRSystemBaseException
from starlette import status


class JobRequirementBlackListService(BaseService[JobRequirementBlackList]):
    def __init__(self):
        super().__init__(JobRequirementBlackList)

    def create_job_requirement_black_list(
        self, db: Session, data: JobRequirementBlackListCreateRequest
    ) -> JobRequirementBlackList:
        """Create a new job requirement black list association with validation"""
        # Check if association already exists
        existing_association = (
            db.query(JobRequirementBlackList)
            .filter(
                and_(
                    JobRequirementBlackList.job_requirement_id
                    == data.job_requirement_id,
                    JobRequirementBlackList.black_list_id == data.black_list_id,
                    JobRequirementBlackList.deleted_at.is_(None),
                )
            )
            .first()
        )

        if existing_association:
            raise HRSystemBaseException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="This black list entry is already associated with the job requirement",
            )

        association_dict = data.model_dump()
        return self.create(db, association_dict)

    def update_job_requirement_black_list(
        self,
        db: Session,
        association_id: int,
        data: JobRequirementBlackListUpdateRequest,
    ) -> Optional[JobRequirementBlackList]:
        """Update job requirement black list association"""
        association_dict = data.model_dump(exclude_unset=True)
        return self.update(db, association_id, association_dict)

    def get_black_lists_by_job_requirement(
        self, db: Session, job_requirement_id: int
    ) -> List[JobRequirementBlackList]:
        """Get all black list entries for a specific job requirement"""
        return (
            db.query(JobRequirementBlackList)
            .filter(
                and_(
                    JobRequirementBlackList.job_requirement_id == job_requirement_id,
                    JobRequirementBlackList.deleted_at.is_(None),
                )
            )
            .all()
        )

    def get_job_requirements_by_black_list(
        self, db: Session, black_list_id: int
    ) -> List[JobRequirementBlackList]:
        """Get all job requirements that have a specific black list entry"""
        return (
            db.query(JobRequirementBlackList)
            .filter(
                and_(
                    JobRequirementBlackList.black_list_id == black_list_id,
                    JobRequirementBlackList.deleted_at.is_(None),
                )
            )
            .all()
        )

    def remove_black_list_from_job_requirement(
        self, db: Session, job_requirement_id: int, black_list_id: int
    ) -> bool:
        """Remove a black list entry from a job requirement"""
        association = (
            db.query(JobRequirementBlackList)
            .filter(
                and_(
                    JobRequirementBlackList.job_requirement_id == job_requirement_id,
                    JobRequirementBlackList.black_list_id == black_list_id,
                    JobRequirementBlackList.deleted_at.is_(None),
                )
            )
            .first()
        )

        if association:
            return self.soft_delete(db, association.id)
        return False


# Create singleton instance
job_requirement_black_list_service = JobRequirementBlackListService()
