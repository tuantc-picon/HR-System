from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from model.application.applications import Application
from services.base_service import BaseService
from schema.request.application_schemas import (
    ApplicationCreateRequest,
    ApplicationUpdateRequest,
)


class ApplicationService(BaseService[Application]):
    def __init__(self):
        super().__init__(Application)

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


# Create singleton instance
application_service = ApplicationService()
