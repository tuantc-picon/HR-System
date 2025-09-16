from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SkillResponse(BaseModel):
    id: int
    job_role_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
