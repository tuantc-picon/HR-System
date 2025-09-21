from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from .resume_schemas import ResumeResponse


class CandidateResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    birth_date: str
    phone_number: str
    is_blocklisted: bool
    note: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    resumes: Optional[List[ResumeResponse]] = None

    class Config:
        from_attributes = True


class CandidateWithResumeResponse(BaseModel):
    """Response model for candidate creation with CV upload"""

    candidate: CandidateResponse
    resume: Optional[ResumeResponse] = None
    upload_info: Optional[dict] = None

    class Config:
        from_attributes = True
