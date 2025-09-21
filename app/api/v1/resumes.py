from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.common.database import get_db_session
from services.resume_service import resume_service
from schema.request.resume_schemas import ResumeCreateRequest, ResumeUpdateRequest
from schema.response.resume_schemas import ResumeResponse

router = APIRouter()


@router.post("/", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
def create_resume(
    resume_data: ResumeCreateRequest, db: Session = Depends(get_db_session)
):
    """Create a new resume"""
    resume = resume_service.create_resume(db, resume_data)
    return resume


@router.get("/", response_model=List[ResumeResponse])
def get_resumes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    """Get all resumes"""
    resumes = resume_service.get_all(db, skip=skip, limit=limit)
    return resumes


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(resume_id: int, db: Session = Depends(get_db_session)):
    """Get resume by ID"""
    resume = resume_service.get_by_id(db, resume_id)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )
    return resume


@router.put("/{resume_id}", response_model=ResumeResponse)
def update_resume(
    resume_id: int,
    resume_data: ResumeUpdateRequest,
    db: Session = Depends(get_db_session),
):
    """Update resume"""
    resume = resume_service.update_resume(db, resume_id, resume_data)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )
    return resume


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(resume_id: int, db: Session = Depends(get_db_session)):
    """Soft delete resume"""
    success = resume_service.soft_delete(db, resume_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )


@router.get("/candidate/{candidate_id}", response_model=List[ResumeResponse])
def get_resumes_by_candidate(candidate_id: int, db: Session = Depends(get_db_session)):
    """Get all resumes for a specific candidate"""
    resumes = resume_service.get_resumes_by_candidate(db, candidate_id)
    return resumes


@router.get("/file-path/{file_path:path}", response_model=ResumeResponse)
def get_resume_by_file_path(file_path: str, db: Session = Depends(get_db_session)):
    """Get resume by file path"""
    resume = resume_service.get_resume_by_file_path(db, file_path)
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
        )
    return resume
