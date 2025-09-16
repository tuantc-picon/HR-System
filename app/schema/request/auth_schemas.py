from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    """Schema for login request"""
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str


class RegisterRequest(BaseModel):
    """Schema for user registration request"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    birth_date: str
    role_id: Optional[int] = 1
