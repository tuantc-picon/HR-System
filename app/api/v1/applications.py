from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.common.database import get_db_session
from services.application_service import application_service
from schema.request.application_schemas import (
    ApplicationCreateRequest,
    ApplicationUpdateRequest,
)
from schema.response.application_schemas import ApplicationResponse

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
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)
):
    """Get all applications"""
    applications = application_service.get_all(db, skip=skip, limit=limit)
    return applications


@router.get("/{application_id}", response_model=ApplicationResponse)
def get_application(application_id: int, db: Session = Depends(get_db_session)):
    """Get application by ID"""
    application = application_service.get_by_id(db, application_id)
    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Application not found"
        )
    return application


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
