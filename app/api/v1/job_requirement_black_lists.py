from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.common.database import get_db_session
from services.job_requirement_black_list_service import (
    job_requirement_black_list_service,
)
from schema.request.job_requirement_black_list_schemas import (
    JobRequirementBlackListCreateRequest,
    JobRequirementBlackListUpdateRequest,
)
from schema.response.job_requirement_black_list_schemas import (
    JobRequirementBlackListResponse,
)
from core.common.exceptions import HRSystemBaseException

router = APIRouter()


@router.post(
    "/",
    response_model=JobRequirementBlackListResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job_requirement_black_list(
    data: JobRequirementBlackListCreateRequest, db: Session = Depends(get_db_session)
):
    """Create a new job requirement black list association"""
    try:
        association = (
            job_requirement_black_list_service.create_job_requirement_black_list(
                db, data
            )
        )
        return association
    except HRSystemBaseException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/", response_model=List[JobRequirementBlackListResponse])
def get_job_requirement_black_lists(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)
):
    """Get all job requirement black list associations"""
    associations = job_requirement_black_list_service.get_all(
        db, skip=skip, limit=limit
    )
    return associations


@router.get("/{association_id}", response_model=JobRequirementBlackListResponse)
def get_job_requirement_black_list(
    association_id: int, db: Session = Depends(get_db_session)
):
    """Get job requirement black list association by ID"""
    association = job_requirement_black_list_service.get_by_id(db, association_id)
    if not association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job requirement black list association not found",
        )
    return association


@router.put("/{association_id}", response_model=JobRequirementBlackListResponse)
def update_job_requirement_black_list(
    association_id: int,
    data: JobRequirementBlackListUpdateRequest,
    db: Session = Depends(get_db_session),
):
    """Update job requirement black list association"""
    association = job_requirement_black_list_service.update_job_requirement_black_list(
        db, association_id, data
    )
    if not association:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job requirement black list association not found",
        )
    return association


@router.delete("/{association_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_requirement_black_list(
    association_id: int, db: Session = Depends(get_db_session)
):
    """Soft delete job requirement black list association"""
    success = job_requirement_black_list_service.soft_delete(db, association_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job requirement black list association not found",
        )


@router.get(
    "/job-requirement/{job_requirement_id}",
    response_model=List[JobRequirementBlackListResponse],
)
def get_black_lists_by_job_requirement(
    job_requirement_id: int, db: Session = Depends(get_db_session)
):
    """Get all black list entries for a specific job requirement"""
    associations = (
        job_requirement_black_list_service.get_black_lists_by_job_requirement(
            db, job_requirement_id
        )
    )
    return associations


@router.get(
    "/black-list/{black_list_id}", response_model=List[JobRequirementBlackListResponse]
)
def get_job_requirements_by_black_list(
    black_list_id: int, db: Session = Depends(get_db_session)
):
    """Get all job requirements that have a specific black list entry"""
    associations = (
        job_requirement_black_list_service.get_job_requirements_by_black_list(
            db, black_list_id
        )
    )
    return associations


@router.delete(
    "/job-requirement/{job_requirement_id}/black-list/{black_list_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_black_list_from_job_requirement(
    job_requirement_id: int, black_list_id: int, db: Session = Depends(get_db_session)
):
    """Remove a black list entry from a job requirement"""
    success = job_requirement_black_list_service.remove_black_list_from_job_requirement(
        db, job_requirement_id, black_list_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Association not found"
        )
