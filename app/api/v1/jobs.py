from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.common.database import get_db_session
from services.job_service import job_service
from schema.request.job_schemas import JobCreateRequest, JobUpdateRequest
from schema.response.job_schemas import JobResponse, JobWithDetailsResponse

router = APIRouter()


@router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(job_data: JobCreateRequest, db: Session = Depends(get_db_session)):
    """Create a new job with requirements, skills, and certificates"""
    job_result = job_service.create_job(db, job_data)
    return job_result["job"]


@router.get("/", response_model=List[JobWithDetailsResponse])
def get_jobs(
    skip: int = 0,
    limit: int = 100,
    include_details: bool = True,
    db: Session = Depends(get_db_session),
):
    """Get all jobs with optional details"""
    if include_details:
        jobs_with_details = job_service.get_all_with_details(db, skip=skip, limit=limit)
        result = []
        for job_data in jobs_with_details:
            # Get additional details for each job
            skills = job_service.get_job_skills(db, job_data["job"].id)
            certificates = job_service.get_job_certificates(db, job_data["job"].id)
            black_lists = job_service.get_job_black_lists(db, job_data["job"].id)

            # Build response
            response_data = {
                **job_data["job"].__dict__,
                "job_role": job_data["job_role"],
                "job_requirements": job_data["job_requirements"],
                "skills": skills,
                "certificates": certificates,
                "black_lists": black_lists,
            }
            result.append(JobWithDetailsResponse(**response_data))
        return result
    else:
        jobs = job_service.get_all(db, skip=skip, limit=limit)
        return [JobResponse.model_validate(job) for job in jobs]


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int, include_details: bool = False, db: Session = Depends(get_db_session)
):
    """Get job by ID with optional details"""
    if include_details:
        job = job_service.get_job_with_details(db, job_id)
    else:
        job = job_service.get_by_id(db, job_id)

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    return job


@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int, job_data: JobUpdateRequest, db: Session = Depends(get_db_session)
):
    """Update job with requirements, skills, and certificates"""
    job_result = job_service.update_job(db, job_id, job_data)
    if not job_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    return job_result["job"]


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id: int, db: Session = Depends(get_db_session)):
    """Soft delete job"""
    success = job_service.soft_delete(db, job_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )


@router.get("/area/{area}", response_model=List[JobResponse])
def get_jobs_by_area(area: int, db: Session = Depends(get_db_session)):
    """Get jobs by area (1: Da Nang, 3: Ho Chi Minh, 5: Hanoi)"""
    jobs = job_service.get_jobs_by_area(db, area)
    return jobs


@router.get("/employment-type/{employment_type}", response_model=List[JobResponse])
def get_jobs_by_employment_type(
    employment_type: int, db: Session = Depends(get_db_session)
):
    """Get jobs by employment type"""
    jobs = job_service.get_jobs_by_employment_type(db, employment_type)
    return jobs


@router.get("/creator/{created_by}", response_model=List[JobResponse])
def get_jobs_by_creator(created_by: int, db: Session = Depends(get_db_session)):
    """Get jobs created by a specific user"""
    jobs = job_service.get_jobs_by_creator(db, created_by)
    return jobs


@router.get("/search/{title_keyword}", response_model=List[JobResponse])
def search_jobs_by_title(title_keyword: str, db: Session = Depends(get_db_session)):
    """Search jobs by title keyword"""
    jobs = job_service.search_jobs_by_title(db, title_keyword)
    return jobs


@router.get("/{job_id}/details", response_model=JobWithDetailsResponse)
def get_job_with_details(job_id: int, db: Session = Depends(get_db_session)):
    """Get job with full details including job role, requirements, skills, certificates, and black lists"""
    job_details = job_service.get_job_with_details(db, job_id)
    if not job_details:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )

    # Get additional details
    skills = job_service.get_job_skills(db, job_id)
    certificates = job_service.get_job_certificates(db, job_id)
    black_lists = job_service.get_job_black_lists(db, job_id)

    # Build response
    response_data = {
        **job_details["job"].__dict__,
        "job_role": job_details["job_role"],
        "job_requirements": job_details["job_requirements"],
        "skills": skills,
        "certificates": certificates,
        "black_lists": black_lists,
    }

    return JobWithDetailsResponse(**response_data)


@router.get("/role/{job_role_id}", response_model=List[JobResponse])
def get_jobs_by_role(job_role_id: int, db: Session = Depends(get_db_session)):
    """Get jobs by job role"""
    jobs = job_service.get_jobs_by_role(db, job_role_id)
    return jobs
