from pydantic import BaseModel
from typing import Optional


class RoleCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: Optional[bool] = True


class RoleUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
