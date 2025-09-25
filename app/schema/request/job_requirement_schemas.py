from pydantic import BaseModel
from typing import Optional, List


class JobRequirementCreateRequest(BaseModel):
    job_role_id: Optional[int] = None  # Reference to job role master data
    skill_ids: Optional[List[int]] = []  # Selected skills from job role (subset or all)
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    note: Optional[str] = None
    certificate_ids: Optional[
        List[int]
    ] = []  # Certificates required for this requirement
    black_list_ids: Optional[List[int]] = []  # Black list items for this requirement


class JobRequirementUpdateRequest(BaseModel):
    job_role_id: Optional[int] = None  # Reference to job role master data
    skill_ids: Optional[
        List[int]
    ] = None  # Selected skills from job role (subset or all)
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    note: Optional[str] = None
    certificate_ids: Optional[List[int]] = None
    black_list_ids: Optional[List[int]] = None
