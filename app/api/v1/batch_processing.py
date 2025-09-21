from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from core.common.database import get_db_session
from services.automatic_application_service import automatic_application_service
from core.common.exceptions import HRSystemBaseException

router = APIRouter()


@router.post("/automatic-applications/process", response_model=Dict[str, Any])
def process_automatic_applications(db: Session = Depends(get_db_session)):
    """
    Process automatic application creation for all eligible jobs and candidates.

    This endpoint triggers the batch processing system that:
    1. Finds all open jobs (status = 3) with valid deadlines
    2. Finds all eligible candidates (not blocklisted, created after job opening)
    3. Creates applications for candidates who haven't already applied
    4. Returns detailed statistics about the processing

    Returns:
    - Processing statistics including jobs processed, applications created, etc.
    """
    try:
        result = automatic_application_service.process_automatic_applications(db)
        return {
            "success": True,
            "message": "Automatic application processing completed",
            "data": result,
        }
    except HRSystemBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/automatic-applications/summary", response_model=Dict[str, Any])
def get_automatic_applications_summary(db: Session = Depends(get_db_session)):
    """
    Get a summary of the current state for automatic application processing.

    This endpoint provides information about:
    - Number of eligible jobs (open status, valid deadline)
    - Number of eligible candidates (not blocklisted, created after job opening)
    - Number of potential new applications that could be created

    Returns:
    - Summary statistics without actually creating applications
    """
    try:
        result = automatic_application_service.get_processing_summary(db)
        return {
            "success": True,
            "message": "Summary retrieved successfully",
            "data": result,
        }
    except HRSystemBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/automatic-applications/eligible-jobs", response_model=Dict[str, Any])
def get_eligible_jobs(db: Session = Depends(get_db_session)):
    """
    Get all jobs that are eligible for automatic application creation.

    Returns:
    - List of jobs with status = OPEN (3) and valid deadlines
    """
    try:
        jobs = automatic_application_service.get_eligible_jobs(db)
        job_data = []

        for job in jobs:
            job_data.append(
                {
                    "id": job.id,
                    "title": job.title,
                    "status": job.status,
                    "application_deadline": job.application_deadline,
                    "created_at": job.created_at,
                    "area": job.area,
                    "employment_type": job.employment_type,
                }
            )

        return {
            "success": True,
            "message": f"Found {len(jobs)} eligible jobs",
            "data": {"jobs": job_data, "count": len(jobs)},
        }
    except HRSystemBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/automatic-applications/eligible-candidates/{job_id}",
    response_model=Dict[str, Any],
)
def get_eligible_candidates_for_job(job_id: int, db: Session = Depends(get_db_session)):
    """
    Get all candidates that are eligible for automatic application to a specific job.

    Args:
    - job_id: The ID of the job to check candidates for

    Returns:
    - List of candidates eligible for the specified job
    """
    try:
        # First get the job
        from model.job.jobs import Job

        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        candidates = automatic_application_service.get_eligible_candidates(db, job)
        candidate_data = []

        for candidate in candidates:
            # Check if candidate already applied
            has_applied = automatic_application_service.has_existing_application(
                db, job_id, candidate.id
            )

            candidate_data.append(
                {
                    "id": candidate.id,
                    "email": candidate.email,
                    "first_name": candidate.first_name,
                    "last_name": candidate.last_name,
                    "is_blocklisted": candidate.is_blocklisted,
                    "created_at": candidate.created_at,
                    "has_existing_application": has_applied,
                }
            )

        return {
            "success": True,
            "message": f"Found {len(candidates)} eligible candidates for job {job_id}",
            "data": {
                "job": {"id": job.id, "title": job.title, "created_at": job.created_at},
                "candidates": candidate_data,
                "count": len(candidates),
            },
        }
    except HRSystemBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
