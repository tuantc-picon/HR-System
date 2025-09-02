from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.common.database import get_db_session
from services.job_requirement_certificate_service import job_requirement_certificate_service
from schema.request.job_requirement_certificate_schemas import JobRequirementCertificateCreateRequest, JobRequirementCertificateUpdateRequest
from schema.response.job_requirement_certificate_schemas import JobRequirementCertificateResponse
from core.common.exceptions import HRSystemBaseException

router = APIRouter()


@router.post("/", response_model=JobRequirementCertificateResponse, status_code=status.HTTP_201_CREATED)
def create_job_requirement_certificate(
    data: JobRequirementCertificateCreateRequest,
    db: Session = Depends(get_db_session)
):
    """Create a new job requirement certificate association"""
    try:
        association = job_requirement_certificate_service.create_job_requirement_certificate(db, data)
        return association
    except HRSystemBaseException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/", response_model=List[JobRequirementCertificateResponse])
def get_job_requirement_certificates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session)
):
    """Get all job requirement certificate associations"""
    associations = job_requirement_certificate_service.get_all(db, skip=skip, limit=limit)
    return associations


@router.get("/{association_id}", response_model=JobRequirementCertificateResponse)
def get_job_requirement_certificate(
    association_id: int,
    db: Session = Depends(get_db_session)
):
    """Get job requirement certificate association by ID"""
    association = job_requirement_certificate_service.get_by_id(db, association_id)
    if not association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job requirement certificate association not found"
        )
    return association


@router.put("/{association_id}", response_model=JobRequirementCertificateResponse)
def update_job_requirement_certificate(
    association_id: int,
    data: JobRequirementCertificateUpdateRequest,
    db: Session = Depends(get_db_session)
):
    """Update job requirement certificate association"""
    association = job_requirement_certificate_service.update_job_requirement_certificate(db, association_id, data)
    if not association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job requirement certificate association not found"
        )
    return association


@router.delete("/{association_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_requirement_certificate(
    association_id: int,
    db: Session = Depends(get_db_session)
):
    """Soft delete job requirement certificate association"""
    success = job_requirement_certificate_service.soft_delete(db, association_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job requirement certificate association not found"
        )


@router.get("/job-requirement/{job_requirement_id}", response_model=List[JobRequirementCertificateResponse])
def get_certificates_by_job_requirement(
    job_requirement_id: int,
    db: Session = Depends(get_db_session)
):
    """Get all certificates for a specific job requirement"""
    associations = job_requirement_certificate_service.get_certificates_by_job_requirement(db, job_requirement_id)
    return associations


@router.get("/certificate/{certificate_id}", response_model=List[JobRequirementCertificateResponse])
def get_job_requirements_by_certificate(
    certificate_id: int,
    db: Session = Depends(get_db_session)
):
    """Get all job requirements that require a specific certificate"""
    associations = job_requirement_certificate_service.get_job_requirements_by_certificate(db, certificate_id)
    return associations


@router.delete("/job-requirement/{job_requirement_id}/certificate/{certificate_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_certificate_from_job_requirement(
    job_requirement_id: int,
    certificate_id: int,
    db: Session = Depends(get_db_session)
):
    """Remove a certificate from a job requirement"""
    success = job_requirement_certificate_service.remove_certificate_from_job_requirement(db, job_requirement_id, certificate_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Association not found"
        )
