from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
import urllib.parse


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
    job_role_id: Optional[int] = None  # Inherited from parent job - MUST be included
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
    status: int
    application_deadline: Optional[datetime] = None
    recruitment_count: int
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


class ResumeFileInfo(BaseModel):
    """Resume file information for job response"""

    id: int
    candidate_id: int
    file_path: str
    file_url: Optional[str] = None  # For Google Drive files or processed local URLs
    storage_type: str  # "local" or "google_drive"
    note: Optional[str] = None
    created_at: datetime

    # File serving URLs
    download_url: Optional[str] = None
    view_url: Optional[str] = None
    info_url: Optional[str] = None

    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        # Generate file serving URLs
        if self.file_path:
            # URL encode the file path to handle special characters
            encoded_path = urllib.parse.quote(self.file_path, safe="/")
            self.download_url = f"/api/v1/files/download/{encoded_path}"
            self.view_url = f"/api/v1/files/view/{encoded_path}"
            self.info_url = f"/api/v1/files/resume-info/{encoded_path}"


class ApplicationResumeInfo(BaseModel):
    """Application with resume information for job response"""

    application_id: int
    candidate_id: int
    candidate_name: str
    application_status: int
    resume: Optional[ResumeFileInfo] = None

    class Config:
        from_attributes = True


class JobWithDetailsResponse(BaseModel):
    """Extended job response with full details"""

    id: int
    title: str
    job_role_id: Optional[int] = None
    area: int
    employment_type: int
    status: int
    application_deadline: Optional[datetime] = None
    recruitment_count: int
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


class JobWithResumesResponse(BaseModel):
    """Extended job response with full details including resume files"""

    id: int
    title: str
    job_role_id: Optional[int] = None
    area: int
    employment_type: int
    status: int
    application_deadline: Optional[datetime] = None
    recruitment_count: int
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
    applications_with_resumes: List[ApplicationResumeInfo] = []

    class Config:
        from_attributes = True
