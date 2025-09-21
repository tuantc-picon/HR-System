from pydantic import BaseModel
from typing import Dict, Any


class UserInfo(BaseModel):
    """User information schema"""

    id: int
    email: str
    first_name: str
    last_name: str
    role_id: int


class LoginResponse(BaseModel):
    """Schema for login response"""

    access_token: str
    refresh_token: str
    token_type: str
    user: UserInfo


class RefreshTokenResponse(BaseModel):
    """Schema for refresh token response"""

    access_token: str
    token_type: str
