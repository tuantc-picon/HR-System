from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from core.common.database import get_db_session
from services.application_service import application_service
from schema.request.application_schemas import (
    ApplicationCreateRequest,
    ApplicationUpdateRequest,
)
from schema.response.application_schemas import (
    ApplicationResponse,
    ApplicationDetailResponse,
)

router = APIRouter()


@router.post(
    "/", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED
)
def create_application(
    application_data: ApplicationCreateRequest, db: Session = Depends(get_db_session)
):
    """Create a new application"""
    application = application_service.create_application(db, application_data)
    return application


@router.get("/", response_model=List[ApplicationResponse])
def get_applications(
    skip: int = 0,
    limit: int = 100,
    status: Optional[int] = None,
    job_id: Optional[int] = None,
    candidate_id: Optional[int] = None,
    resume_id: Optional[int] = None,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    db: Session = Depends(get_db_session),
):
    """Get all applications with optional filtering"""
    # Build filter parameters
    filters = {}
    if status is not None:
        filters["status"] = status
    if job_id is not None:
        filters["job_id"] = job_id
    if candidate_id is not None:
        filters["candidate_id"] = candidate_id
    if resume_id is not None:
        filters["resume_id"] = resume_id

    # Date range filtering will be handled separately in the service
    date_filters = {}
    if created_after:
        date_filters["created_after"] = created_after
    if created_before:
        date_filters["created_before"] = created_before

    applications = application_service.get_all(
        db, skip=skip, limit=limit, filters=filters, date_filters=date_filters
    )
    return applications


@router.get("/{application_id}", response_model=ApplicationDetailResponse)
def get_application_details(application_id: int, db: Session = Depends(get_db_session)):
    """Get comprehensive application details including job, candidate, and resume information"""
    application_details = application_service.get_application_with_details(
        db, application_id
    )
    if not application_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )
    return application_details


@router.put("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: int,
    application_data: ApplicationUpdateRequest,
    db: Session = Depends(get_db_session),
):
    """Update application"""
    application = application_service.update_application(
        db, application_id, application_data
    )
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )
    return application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: int, db: Session = Depends(get_db_session)):
    """Soft delete application"""
    success = application_service.soft_delete(db, application_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )


@router.get("/job/{job_id}", response_model=List[ApplicationResponse])
def get_applications_by_job(job_id: int, db: Session = Depends(get_db_session)):
    """Get all applications for a specific job"""
    applications = application_service.get_applications_by_job(db, job_id)
    return applications


@router.get("/candidate/{candidate_id}", response_model=List[ApplicationResponse])
def get_applications_by_candidate(
    candidate_id: int, db: Session = Depends(get_db_session)
):
    """Get all applications by a specific candidate"""
    applications = application_service.get_applications_by_candidate(db, candidate_id)
    return applications


@router.get("/status/{status_value}", response_model=List[ApplicationResponse])
def get_applications_by_status(
    status_value: int, db: Session = Depends(get_db_session)
):
    """Get applications by status"""
    applications = application_service.get_applications_by_status(db, status_value)
    return applications


@router.get("/resume/{resume_id}", response_model=List[ApplicationResponse])
def get_applications_by_resume(resume_id: int, db: Session = Depends(get_db_session)):
    """Get applications using a specific resume"""
    applications = application_service.get_applications_by_resume(db, resume_id)
    return applications


@router.patch("/{application_id}/status", response_model=ApplicationResponse)
def update_application_status(
    application_id: int,
    status_value: int,
    updated_by: int = None,
    db: Session = Depends(get_db_session),
):
    """Update application status"""
    application = application_service.update_application_status(
        db, application_id, status_value, updated_by
    )
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )
    return application
