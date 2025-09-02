from pydantic import BaseModel, EmailStr
from typing import Optional


class CandidateCreateRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    birth_date: str
    phone_number: str
    note: Optional[str] = None


class CandidateUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    birth_date: Optional[str] = None
    phone_number: Optional[str] = None
    note: Optional[str] = None
