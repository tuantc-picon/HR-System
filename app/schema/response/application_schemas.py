from pydantic import BaseModel
from datetime import datetime
from typing import Optional


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
