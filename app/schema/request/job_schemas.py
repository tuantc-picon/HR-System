from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


from .job_requirement_schemas import JobRequirementCreateRequest


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
        extra = "forbid"  # Forbid extra fields


class JobUpdateRequest(BaseModel):
    title: Optional[str] = None
    # No job_role_id or skill_ids at job level - managed at requirement level
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
        extra = "forbid"  # Forbid extra fields
