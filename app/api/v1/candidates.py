from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.common.database import get_db_session
from services.candidate_service import candidate_service
from schema.request.candidate_schemas import CandidateCreateRequest, CandidateUpdateRequest
from schema.response.candidate_schemas import CandidateResponse
from core.common.exceptions import HRSystemBaseException

router = APIRouter()


@router.post("/", response_model=CandidateResponse, status_code=status.HTTP_201_CREATED)
def create_candidate(
    candidate_data: CandidateCreateRequest,
    db: Session = Depends(get_db_session)
):
    """Create a new candidate"""
    try:
        candidate = candidate_service.create_candidate(db, candidate_data)
        return candidate
    except HRSystemBaseException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/", response_model=List[CandidateResponse])
def get_candidates(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session)
):
    """Get all candidates"""
    candidates = candidate_service.get_all(db, skip=skip, limit=limit)
    return candidates


@router.get("/{candidate_id}", response_model=CandidateResponse)
def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db_session)
):
    """Get candidate by ID"""
    candidate = candidate_service.get_by_id(db, candidate_id)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    return candidate


@router.put("/{candidate_id}", response_model=CandidateResponse)
def update_candidate(
    candidate_id: int,
    candidate_data: CandidateUpdateRequest,
    db: Session = Depends(get_db_session)
):
    """Update candidate"""
    try:
        candidate = candidate_service.update_candidate(db, candidate_id, candidate_data)
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate not found"
            )
        return candidate
    except HRSystemBaseException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.delete("/{candidate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_candidate(
    candidate_id: int,
    db: Session = Depends(get_db_session)
):
    """Soft delete candidate"""
    success = candidate_service.soft_delete(db, candidate_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )


@router.get("/email/{email}", response_model=CandidateResponse)
def get_candidate_by_email(
    email: str,
    db: Session = Depends(get_db_session)
):
    """Get candidate by email"""
    candidate = candidate_service.get_candidate_by_email(db, email)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    return candidate


@router.get("/search/{name_keyword}", response_model=List[CandidateResponse])
def search_candidates_by_name(
    name_keyword: str,
    db: Session = Depends(get_db_session)
):
    """Search candidates by first name or last name"""
    candidates = candidate_service.search_candidates_by_name(db, name_keyword)
    return candidates


@router.get("/phone/{phone_number}", response_model=CandidateResponse)
def get_candidate_by_phone(
    phone_number: str,
    db: Session = Depends(get_db_session)
):
    """Get candidate by phone number"""
    candidate = candidate_service.get_candidates_by_phone(db, phone_number)
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found"
        )
    return candidate
