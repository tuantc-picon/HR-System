from pydantic import BaseModel
from typing import Optional


class JobCreateRequest(BaseModel):
    title: str
    area: Optional[int] = 1  # 1: Da Nang, 3: Ho Chi Minh, 5: Hanoi
    employment_type: Optional[int] = 1  # 1: Full-time, 3: Part-time, 5: Fresher, 7: Internship, 9: Vendor
    description: Optional[str] = None
    source: Optional[int] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None


class JobUpdateRequest(BaseModel):
    title: Optional[str] = None
    area: Optional[int] = None
    employment_type: Optional[int] = None
    description: Optional[str] = None
    source: Optional[int] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
