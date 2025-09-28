from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import urllib.parse


class ResumeResponse(BaseModel):
    id: int
    candidate_id: int
    file_path: str
    note: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    # Computed fields for file serving
    download_url: Optional[str] = None
    view_url: Optional[str] = None
    storage_type: Optional[str] = None

    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        # Generate download and view URLs
        if self.file_path:
            # URL encode the file path to handle special characters
            encoded_path = urllib.parse.quote(self.file_path, safe="/")
            self.download_url = f"/api/v1/files/download/{encoded_path}"
            self.view_url = f"/api/v1/files/view/{encoded_path}"

            # Determine storage type
            self.storage_type = (
                "google_drive" if self.file_path.startswith("http") else "local"
            )


class ResumeWithUrlsResponse(BaseModel):
    """Enhanced resume response with downloadable URLs"""

    id: int
    candidate_id: int
    file_path: str
    note: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    # File serving URLs
    download_url: str
    view_url: str
    info_url: str
    storage_type: str

    class Config:
        from_attributes = True

    @classmethod
    def from_resume(cls, resume, base_url: str = "/api/v1/files"):
        """Create ResumeWithUrlsResponse from Resume model"""
        # URL encode the file path to handle special characters
        encoded_path = urllib.parse.quote(resume.file_path, safe="/")

        return cls(
            id=resume.id,
            candidate_id=resume.candidate_id,
            file_path=resume.file_path,
            note=resume.note,
            created_at=resume.created_at,
            updated_at=resume.updated_at,
            deleted_at=resume.deleted_at,
            download_url=f"{base_url}/download/{encoded_path}",
            view_url=f"{base_url}/view/{encoded_path}",
            info_url=f"{base_url}/resume-info/{encoded_path}",
            storage_type="google_drive"
            if resume.file_path.startswith("http")
            else "local",
        )
