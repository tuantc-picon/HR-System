from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.common.database import get_db_session
from services.job_skill_service import job_skill_service
from schema.request.job_skill_schemas import (
    JobSkillCreateRequest,
    JobSkillBulkCreateRequest,
    JobSkillBulkDeleteRequest,
)
from schema.response.job_skill_schemas import JobSkillResponse
from schema.response.skill_schemas import SkillResponse

router = APIRouter()


@router.post("/", response_model=JobSkillResponse, status_code=status.HTTP_201_CREATED)
def add_skill_to_job(
    job_skill_data: JobSkillCreateRequest, db: Session = Depends(get_db_session)
):
    """Add a skill to a job"""
    job_skill = job_skill_service.add_skill_to_job(
        db, job_skill_data.job_id, job_skill_data.skill_id
    )
    return job_skill


@router.post(
    "/bulk", response_model=List[JobSkillResponse], status_code=status.HTTP_201_CREATED
)
def bulk_add_skills_to_job(
    bulk_data: JobSkillBulkCreateRequest, db: Session = Depends(get_db_session)
):
    """Add multiple skills to a job (replaces existing skills)"""
    job_skills = job_skill_service.bulk_add_skills_to_job(
        db, bulk_data.job_id, bulk_data.skill_ids
    )
    return job_skills


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def remove_skill_from_job(
    job_skill_data: JobSkillCreateRequest, db: Session = Depends(get_db_session)
):
    """Remove a skill from a job"""
    success = job_skill_service.remove_skill_from_job(
        db, job_skill_data.job_id, job_skill_data.skill_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job skill association not found",
        )


@router.delete("/bulk", status_code=status.HTTP_200_OK)
def bulk_remove_skills_from_job(
    bulk_data: JobSkillBulkDeleteRequest, db: Session = Depends(get_db_session)
):
    """Remove multiple skills from a job"""
    deleted_count = job_skill_service.bulk_remove_skills_from_job(
        db, bulk_data.job_id, bulk_data.skill_ids
    )
    return {"deleted_count": deleted_count}


@router.get("/job/{job_id}/skills", response_model=List[SkillResponse])
def get_skills_for_job(job_id: int, db: Session = Depends(get_db_session)):
    """Get all skills associated with a job"""
    skills = job_skill_service.get_skills_for_job(db, job_id)
    return skills


@router.get(
    "/job-role/{job_role_id}/available-skills", response_model=List[SkillResponse]
)
def get_available_skills_for_job_role(
    job_role_id: int, db: Session = Depends(get_db_session)
):
    """Get all skills available for selection from a job role"""
    skills = job_skill_service.get_available_skills_for_job_role(db, job_role_id)
    return skills


@router.get("/job/{job_id}/count")
def count_skills_for_job(job_id: int, db: Session = Depends(get_db_session)):
    """Count the number of skills associated with a job"""
    count = job_skill_service.count_skills_for_job(db, job_id)
    return {"job_id": job_id, "skill_count": count}
