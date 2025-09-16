from pydantic import BaseModel
from typing import Optional, List


class JobRequirementCreateRequest(BaseModel):
    """Schema for creating job requirements"""
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    note: Optional[str] = None
    certificate_ids: Optional[List[int]] = []  # List of certificate IDs required
    black_list_ids: Optional[List[int]] = []  # List of black list IDs to check


class JobCreateRequest(BaseModel):
    title: str
    job_role_id: Optional[int] = None  # Reference to job role master data
    area: Optional[int] = 1  # 1: Da Nang, 3: Ho Chi Minh, 5: Hanoi
    employment_type: Optional[int] = 1  # 1: Full-time, 3: Part-time, 5: Fresher, 7: Internship, 9: Vendor
    description: Optional[str] = None
    source: Optional[int] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    job_requirements: Optional[List[JobRequirementCreateRequest]] = []
    skill_ids: Optional[List[int]] = []  # List of skill IDs required for this job
    include_black_list_check: Optional[bool] = False  # Flag to indicate if black list checks should be applied


class JobUpdateRequest(BaseModel):
    title: Optional[str] = None
    job_role_id: Optional[int] = None
    area: Optional[int] = None
    employment_type: Optional[int] = None
    description: Optional[str] = None
    source: Optional[int] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    job_requirements: Optional[List[JobRequirementCreateRequest]] = None
    skill_ids: Optional[List[int]] = None
    include_black_list_check: Optional[bool] = None
