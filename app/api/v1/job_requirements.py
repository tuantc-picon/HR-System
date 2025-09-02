from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.common.database import get_db_session
from services.job_requirement_service import job_requirement_service
from schema.request.job_requirement_schemas import JobRequirementCreateRequest, JobRequirementUpdateRequest
from schema.response.job_requirement_schemas import JobRequirementResponse
from core.common.exceptions import HRSystemBaseException

router = APIRouter()


@router.post("/", response_model=JobRequirementResponse, status_code=status.HTTP_201_CREATED)
def create_job_requirement(
    job_requirement_data: JobRequirementCreateRequest,
    db: Session = Depends(get_db_session)
):
    """Create a new job requirement"""
    try:
        job_requirement = job_requirement_service.create_job_requirement(db, job_requirement_data)
        return job_requirement
    except HRSystemBaseException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/", response_model=List[JobRequirementResponse])
def get_job_requirements(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session)
):
    """Get all job requirements"""
    job_requirements = job_requirement_service.get_all(db, skip=skip, limit=limit)
    return job_requirements


@router.get("/{job_requirement_id}", response_model=JobRequirementResponse)
def get_job_requirement(
    job_requirement_id: int,
    db: Session = Depends(get_db_session)
):
    """Get job requirement by ID"""
    job_requirement = job_requirement_service.get_by_id(db, job_requirement_id)
    if not job_requirement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job requirement not found"
        )
    return job_requirement


@router.put("/{job_requirement_id}", response_model=JobRequirementResponse)
def update_job_requirement(
    job_requirement_id: int,
    job_requirement_data: JobRequirementUpdateRequest,
    db: Session = Depends(get_db_session)
):
    """Update job requirement"""
    try:
        job_requirement = job_requirement_service.update_job_requirement(db, job_requirement_id, job_requirement_data)
        if not job_requirement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job requirement not found"
            )
        return job_requirement
    except HRSystemBaseException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.delete("/{job_requirement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_requirement(
    job_requirement_id: int,
    db: Session = Depends(get_db_session)
):
    """Soft delete job requirement"""
    success = job_requirement_service.soft_delete(db, job_requirement_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job requirement not found"
        )


@router.get("/job/{job_id}", response_model=List[JobRequirementResponse])
def get_requirements_by_job(
    job_id: int,
    db: Session = Depends(get_db_session)
):
    """Get all requirements for a specific job"""
    job_requirements = job_requirement_service.get_requirements_by_job(db, job_id)
    return job_requirements
