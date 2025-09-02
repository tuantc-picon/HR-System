from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CertificateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    category: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
