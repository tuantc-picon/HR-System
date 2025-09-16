from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class JobRoleInfo(BaseModel):
    """Basic job role information for job response"""
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class JobRequirementInfo(BaseModel):
    """Basic job requirement information for job response"""
    id: int
    min_experience: Optional[int] = None
    max_experience: Optional[int] = None
    min_salary: Optional[int] = None
    max_salary: Optional[int] = None
    note: Optional[str] = None

    class Config:
        from_attributes = True


class JobResponse(BaseModel):
    id: int
    title: str
    job_role_id: Optional[int] = None
    area: int
    employment_type: int
    description: Optional[str] = None
    source: Optional[int] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SkillInfo(BaseModel):
    """Basic skill information for job response"""
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class CertificateInfo(BaseModel):
    """Basic certificate information for job response"""
    id: int
    name: str
    description: Optional[str] = None
    category: int
    is_active: bool

    class Config:
        from_attributes = True


class BlackListInfo(BaseModel):
    """Basic black list information for job response"""
    id: int
    name: str
    description: Optional[str] = None
    category: int
    is_active: bool

    class Config:
        from_attributes = True


class JobWithDetailsResponse(BaseModel):
    """Extended job response with full details"""
    id: int
    title: str
    job_role_id: Optional[int] = None
    area: int
    employment_type: int
    description: Optional[str] = None
    source: Optional[int] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    job_role: Optional[JobRoleInfo] = None
    job_requirements: List[JobRequirementInfo] = []
    skills: List[SkillInfo] = []
    certificates: List[CertificateInfo] = []
    black_lists: List[BlackListInfo] = []

    class Config:
        from_attributes = True
