from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from model.job.jobs import Job
from services.base_service import BaseService
from schema.request.job_schemas import JobCreateRequest, JobUpdateRequest


class JobService(BaseService[Job]):
    def __init__(self):
        super().__init__(Job)

    def create_job(self, db: Session, job_data: JobCreateRequest) -> Job:
        """Create a new job"""
        job_dict = job_data.model_dump()
        return self.create(db, job_dict)

    def update_job(self, db: Session, job_id: int, job_data: JobUpdateRequest) -> Optional[Job]:
        """Update job"""
        job_dict = job_data.model_dump(exclude_unset=True)
        return self.update(db, job_id, job_dict)

    def get_jobs_by_area(self, db: Session, area: int) -> List[Job]:
        """Get jobs by area (1: Da Nang, 3: Ho Chi Minh, 5: Hanoi)"""
        return db.query(Job).filter(
            and_(
                Job.area == area,
                Job.deleted_at.is_(None)
            )
        ).all()

    def get_jobs_by_employment_type(self, db: Session, employment_type: int) -> List[Job]:
        """Get jobs by employment type"""
        return db.query(Job).filter(
            and_(
                Job.employment_type == employment_type,
                Job.deleted_at.is_(None)
            )
        ).all()

    def get_jobs_by_creator(self, db: Session, created_by: int) -> List[Job]:
        """Get jobs created by a specific user"""
        return db.query(Job).filter(
            and_(
                Job.created_by == created_by,
                Job.deleted_at.is_(None)
            )
        ).all()

    def search_jobs_by_title(self, db: Session, title_keyword: str) -> List[Job]:
        """Search jobs by title keyword"""
        return db.query(Job).filter(
            and_(
                Job.title.ilike(f"%{title_keyword}%"),
                Job.deleted_at.is_(None)
            )
        ).all()


# Create singleton instance
job_service = JobService()
