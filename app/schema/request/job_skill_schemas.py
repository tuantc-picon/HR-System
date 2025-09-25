from pydantic import BaseModel
from typing import List


class JobSkillCreateRequest(BaseModel):
    """Schema for creating a job-skill association"""

    job_id: int
    skill_id: int


class JobSkillBulkCreateRequest(BaseModel):
    """Schema for bulk creating job-skill associations"""

    job_id: int
    skill_ids: List[int]


class JobSkillBulkDeleteRequest(BaseModel):
    """Schema for bulk deleting job-skill associations"""

    job_id: int
    skill_ids: List[int]
