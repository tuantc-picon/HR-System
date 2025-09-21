from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class JobRequirementCreateRequest(BaseModel):
    """Schema for creating job requirements"""

    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    note: Optional[str] = None
    certificate_ids: Optional[List[int]] = []  # List of certificate IDs required
    black_list_ids: Optional[List[int]] = []  # List of black list IDs to check
    skill_ids: Optional[
        List[int]
    ] = []  # List of skill IDs required for this job requirement
    job_role_id: Optional[int] = None  # Reference to job role master data


class JobCreateRequest(BaseModel):
    title: str
    area: Optional[int] = 1  # 1: Da Nang, 3: Ho Chi Minh, 5: Hanoi
    employment_type: Optional[
        int
    ] = 1  # 1: Full-time, 3: Part-time, 5: Fresher, 7: Internship, 9: Vendor
    status: Optional[int] = 1  # 1: Draft, 3: Open, 5: Closed, 7: Cancelled
    application_deadline: Optional[datetime] = None  # Deadline for job applications
    description: Optional[str] = None
    source: Optional[int] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    job_requirements: Optional[List[JobRequirementCreateRequest]] = []
    include_black_list_check: Optional[
        bool
    ] = False  # Flag to indicate if black list checks should be applied

    class Config:
        extra = "forbid"  # Forbid extra fields to ensure skill_ids and job_role_id are not accepted


class JobUpdateRequest(BaseModel):
    title: Optional[str] = None
    area: Optional[int] = None
    employment_type: Optional[int] = None
    status: Optional[int] = None
    application_deadline: Optional[datetime] = None
    description: Optional[str] = None
    source: Optional[int] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    job_requirements: Optional[List[JobRequirementCreateRequest]] = None
    include_black_list_check: Optional[bool] = None

    class Config:
        extra = "forbid"  # Forbid extra fields to ensure skill_ids and job_role_id are not accepted
