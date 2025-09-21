from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.common.database import get_db_session
from services.job_role_service import job_role_service
from schema.request.job_role_schemas import JobRoleCreateRequest, JobRoleUpdateRequest
from schema.response.job_role_schemas import JobRoleResponse

router = APIRouter()


@router.post("", response_model=JobRoleResponse, status_code=status.HTTP_201_CREATED)
def create_job_role(
    job_role_data: JobRoleCreateRequest, db: Session = Depends(get_db_session)
):
    """Create a new job role"""
    job_role = job_role_service.create_job_role(db, job_role_data)
    return job_role


@router.get("", response_model=List[JobRoleResponse])
def get_all_job_roles(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = False,
    db: Session = Depends(get_db_session),
):
    """Get all job roles"""
    if active_only:
        job_roles = job_role_service.get_active_job_roles(db)
    else:
        job_roles = job_role_service.get_all(db, skip=skip, limit=limit)
    return job_roles


@router.get("/{job_role_id}", response_model=JobRoleResponse)
def get_job_role(job_role_id: int, db: Session = Depends(get_db_session)):
    """Get job role by ID"""
    job_role = job_role_service.get_by_id(db, job_role_id)
    if not job_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job role not found"
        )
    return job_role


@router.put("/{job_role_id}", response_model=JobRoleResponse)
def update_job_role(
    job_role_id: int,
    job_role_data: JobRoleUpdateRequest,
    db: Session = Depends(get_db_session),
):
    """Update job role"""
    job_role = job_role_service.update_job_role(db, job_role_id, job_role_data)
    if not job_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job role not found"
        )
    return job_role


@router.delete("/{job_role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_role(job_role_id: int, db: Session = Depends(get_db_session)):
    """Delete job role (soft delete)"""
    success = job_role_service.delete(db, job_role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job role not found"
        )


@router.patch("/{job_role_id}/activate", response_model=JobRoleResponse)
def activate_job_role(job_role_id: int, db: Session = Depends(get_db_session)):
    """Activate job role"""
    job_role = job_role_service.activate_job_role(db, job_role_id)
    if not job_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job role not found"
        )
    return job_role


@router.patch("/{job_role_id}/deactivate", response_model=JobRoleResponse)
def deactivate_job_role(job_role_id: int, db: Session = Depends(get_db_session)):
    """Deactivate job role"""
    job_role = job_role_service.deactivate_job_role(db, job_role_id)
    if not job_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job role not found"
        )
    return job_role


@router.get("/search/{name}", response_model=List[JobRoleResponse])
def search_job_roles_by_name(name: str, db: Session = Depends(get_db_session)):
    """Search job roles by name"""
    job_roles = job_role_service.search_job_roles_by_name(db, name)
    return job_roles
