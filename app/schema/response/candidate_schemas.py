from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class CandidateResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    birth_date: str
    phone_number: str
    note: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True
