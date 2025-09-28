from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from datetime import datetime
from model.application.applications import Application
from model.job.jobs import Job
from model.candidate.candidates import Candidate
from model.candidate.resumes import Resume
from services.base_service import BaseService
from services.job_service import job_service
from schema.request.application_schemas import (
    ApplicationCreateRequest,
    ApplicationUpdateRequest,
)
from schema.response.application_schemas import ApplicationDetailResponse
from schema.response.job_schemas import JobWithDetailsResponse
from schema.response.candidate_schemas import CandidateResponse
from schema.response.resume_schemas import ResumeResponse


class ApplicationService(BaseService[Application]):
    def __init__(self):
        super().__init__(Application)

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        date_filters: Optional[Dict[str, datetime]] = None,
    ) -> List[Application]:
        """Get all applications with optional filtering (excluding soft deleted)"""
        query = db.query(self.model).filter(self.model.deleted_at.is_(None))

        if filters:
            for field, value in filters.items():
                if value is not None and hasattr(self.model, field):
                    # Exact match for all fields
                    query = query.filter(getattr(self.model, field) == value)

        if date_filters:
            if date_filters.get("created_after"):
                query = query.filter(
                    self.model.created_at >= date_filters["created_after"]
                )
            if date_filters.get("created_before"):
                query = query.filter(
                    self.model.created_at <= date_filters["created_before"]
                )

        return query.offset(skip).limit(limit).all()

    def create_application(
        self, db: Session, application_data: ApplicationCreateRequest
    ) -> Application:
        """Create a new application"""
        application_dict = application_data.model_dump()
        return self.create(db, application_dict)

    def update_application(
        self,
        db: Session,
        application_id: int,
        application_data: ApplicationUpdateRequest,
    ) -> Optional[Application]:
        """Update application"""
        application_dict = application_data.model_dump(exclude_unset=True)
        return self.update(db, application_id, application_dict)

    def get_applications_by_job(self, db: Session, job_id: int) -> List[Application]:
        """Get all applications for a specific job"""
        return (
            db.query(Application)
            .filter(
                and_(Application.job_id == job_id, Application.deleted_at.is_(None))
            )
            .all()
        )

    def get_applications_by_candidate(
        self, db: Session, candidate_id: int
    ) -> List[Application]:
        """Get all applications by a specific candidate"""
        return (
            db.query(Application)
            .filter(
                and_(
                    Application.candidate_id == candidate_id,
                    Application.deleted_at.is_(None),
                )
            )
            .all()
        )

    def get_applications_by_status(self, db: Session, status: int) -> List[Application]:
        """Get applications by status"""
        return (
            db.query(Application)
            .filter(
                and_(Application.status == status, Application.deleted_at.is_(None))
            )
            .all()
        )

    def get_applications_by_resume(
        self, db: Session, resume_id: int
    ) -> List[Application]:
        """Get applications using a specific resume"""
        return (
            db.query(Application)
            .filter(
                and_(
                    Application.resume_id == resume_id, Application.deleted_at.is_(None)
                )
            )
            .all()
        )

    def update_application_status(
        self,
        db: Session,
        application_id: int,
        status: int,
        updated_by: Optional[int] = None,
    ) -> Optional[Application]:
        """Update application status"""
        update_data = {"status": status}
        if updated_by:
            update_data["updated_by"] = updated_by
        return self.update(db, application_id, update_data)

    def get_application_with_details(
        self, db: Session, application_id: int
    ) -> Optional[ApplicationDetailResponse]:
        """Get comprehensive application details including job, candidate, and resume information"""
        # Get the application
        application = (
            db.query(Application)
            .filter(
                and_(Application.id == application_id, Application.deleted_at.is_(None))
            )
            .first()
        )

        if not application:
            return None

        # Get job details with all related information
        job_details_dict = job_service.get_job_with_details(db, application.job_id)

        # Get candidate details
        candidate = (
            db.query(Candidate)
            .filter(
                and_(
                    Candidate.id == application.candidate_id,
                    Candidate.deleted_at.is_(None),
                )
            )
            .first()
        )

        # Get resume details
        resume = (
            db.query(Resume)
            .filter(
                and_(Resume.id == application.resume_id, Resume.deleted_at.is_(None))
            )
            .first()
        )

        # Convert to response models
        job_response = None
        if job_details_dict:
            job = job_details_dict["job"]
            job_role = job_details_dict.get("job_role")
            job_requirements = job_details_dict.get("job_requirements", [])

            # Create JobWithDetailsResponse manually
            job_response = JobWithDetailsResponse(
                id=job.id,
                title=job.title,
                job_role_id=job.job_role_id,
                area=job.area,
                employment_type=job.employment_type,
                status=job.status,
                application_deadline=job.application_deadline,
                recruitment_count=job.recruitment_count,
                description=job.description,
                source=job.source,
                created_by=job.created_by,
                updated_by=job.updated_by,
                created_at=job.created_at,
                updated_at=job.updated_at,
                deleted_at=job.deleted_at,
                job_role=job_role,
                job_requirements=job_requirements,
                skills=[],  # Empty for now, can be enhanced later
                certificates=[],  # Empty for now, can be enhanced later
                black_lists=[],  # Empty for now, can be enhanced later
            )

        candidate_response = (
            CandidateResponse.model_validate(candidate) if candidate else None
        )
        resume_response = ResumeResponse.model_validate(resume) if resume else None

        # Create the comprehensive response
        return ApplicationDetailResponse(
            id=application.id,
            job_id=application.job_id,
            candidate_id=application.candidate_id,
            resume_id=application.resume_id,
            status=application.status,
            score_overall=application.score_overall,
            note=application.note,
            created_by=application.created_by,
            updated_by=application.updated_by,
            created_at=application.created_at,
            updated_at=application.updated_at,
            deleted_at=application.deleted_at,
            job=job_response,
            candidate=candidate_response,
            resume=resume_response,
        )


# Create singleton instance
application_service = ApplicationService()
