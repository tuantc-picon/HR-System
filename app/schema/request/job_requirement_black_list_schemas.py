from pydantic import BaseModel
from typing import Optional


class JobRequirementBlackListCreateRequest(BaseModel):
    job_requirement_id: int
    black_list_id: int


class JobRequirementBlackListUpdateRequest(BaseModel):
    job_requirement_id: Optional[int] = None
    black_list_id: Optional[int] = None
