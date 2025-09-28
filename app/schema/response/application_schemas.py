from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from .job_schemas import JobWithDetailsResponse
from .candidate_schemas import CandidateResponse
from .resume_schemas import ResumeResponse


class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    candidate_id: int
    resume_id: int
    status: int
    score_overall: Optional[int] = None
    note: Optional[str] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ApplicationDetailResponse(BaseModel):
    """Comprehensive application response with all related information"""

    id: int
    job_id: int
    candidate_id: int
    resume_id: int
    status: int
    score_overall: Optional[int] = None
    note: Optional[str] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    # Related entities with full details
    job: Optional[JobWithDetailsResponse] = None
    candidate: Optional[CandidateResponse] = None
    resume: Optional[ResumeResponse] = None

    class Config:
        from_attributes = True
