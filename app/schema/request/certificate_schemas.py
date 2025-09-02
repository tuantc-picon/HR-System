from pydantic import BaseModel
from typing import Optional


class CertificateCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True
    category: Optional[int] = 1


class CertificateUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    category: Optional[int] = None
