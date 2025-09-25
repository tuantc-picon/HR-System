from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class JobRequirementResponse(BaseModel):
    id: int
    job_id: int
    job_role_id: Optional[int] = None  # Inherited from parent job
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    note: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
