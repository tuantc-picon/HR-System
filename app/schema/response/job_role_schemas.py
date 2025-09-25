from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class SkillInfo(BaseModel):
    """Basic skill information for job role response"""

    id: int
    name: str
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class JobRoleResponse(BaseModel):
    """Schema for job role response"""

    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JobRoleWithSkillsResponse(BaseModel):
    """Extended job role response with associated skills"""

    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None
    skills: List[SkillInfo] = []

    class Config:
        from_attributes = True
