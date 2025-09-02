from pydantic import BaseModel
from typing import Optional


class ResumeCreateRequest(BaseModel):
    candidate_id: int
    file_path: str
    note: Optional[str] = None


class ResumeUpdateRequest(BaseModel):
    candidate_id: Optional[int] = None
    file_path: Optional[str] = None
    note: Optional[str] = None
