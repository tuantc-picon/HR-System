from pydantic import BaseModel, Field
from typing import Optional


class JobRoleCreateRequest(BaseModel):
    """Schema for creating a new job role"""

    name: str = Field(..., min_length=1, max_length=255, description="Job role name")
    description: Optional[str] = Field(
        None, max_length=1000, description="Job role description"
    )
    is_active: bool = Field(True, description="Whether the job role is active")


class JobRoleUpdateRequest(BaseModel):
    """Schema for updating a job role"""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Job role name"
    )
    description: Optional[str] = Field(
        None, max_length=1000, description="Job role description"
    )
    is_active: Optional[bool] = Field(
        None, description="Whether the job role is active"
    )
