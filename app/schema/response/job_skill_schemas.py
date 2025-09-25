from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class JobSkillResponse(BaseModel):
    """Schema for job-skill association response"""

    id: int
    job_id: int
    skill_id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
