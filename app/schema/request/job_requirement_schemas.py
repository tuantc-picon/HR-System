from pydantic import BaseModel
from typing import Optional


class JobRequirementCreateRequest(BaseModel):
    job_id: int
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    note: Optional[str] = None


class JobRequirementUpdateRequest(BaseModel):
    job_id: Optional[int] = None
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    note: Optional[str] = None
