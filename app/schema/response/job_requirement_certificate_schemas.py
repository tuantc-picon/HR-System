from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class JobRequirementCertificateResponse(BaseModel):
    id: int
    job_requirement_id: int
    certificate_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
