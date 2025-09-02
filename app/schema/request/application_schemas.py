from pydantic import BaseModel
from typing import Optional


class ApplicationCreateRequest(BaseModel):
    job_id: int
    candidate_id: int
    resume_id: int
    status: Optional[int] = 1  # 1: Applied, 3: Screening, 5: Shortlisted, ...
    score_overall: Optional[int] = None
    note: Optional[str] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None


class ApplicationUpdateRequest(BaseModel):
    job_id: Optional[int] = None
    candidate_id: Optional[int] = None
    resume_id: Optional[int] = None
    status: Optional[int] = None
    score_overall: Optional[int] = None
    note: Optional[str] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
