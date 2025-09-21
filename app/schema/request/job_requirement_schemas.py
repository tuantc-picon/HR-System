from pydantic import BaseModel
from typing import Optional, List


class JobRequirementCreateRequest(BaseModel):
    job_id: int
    job_role_id: Optional[int] = None  # Reference to job role master data
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    note: Optional[str] = None
    skill_ids: Optional[
        List[int]
    ] = []  # List of skill IDs required for this job requirement


class JobRequirementUpdateRequest(BaseModel):
    job_id: Optional[int] = None
    job_role_id: Optional[int] = None
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    note: Optional[str] = None
    skill_ids: Optional[List[int]] = None
