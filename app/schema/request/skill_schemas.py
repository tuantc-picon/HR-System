from pydantic import BaseModel
from typing import Optional


class SkillCreateRequest(BaseModel):
    job_role_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True


class SkillUpdateRequest(BaseModel):
    job_role_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
