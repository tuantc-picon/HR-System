from pydantic import BaseModel
from typing import Optional


class JobRequirementCertificateCreateRequest(BaseModel):
    job_requirement_id: int
    certificate_id: int


class JobRequirementCertificateUpdateRequest(BaseModel):
    job_requirement_id: Optional[int] = None
    certificate_id: Optional[int] = None
