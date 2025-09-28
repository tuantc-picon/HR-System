from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Dict, Any

from core.common.database import get_db_session
from services.auth_service import auth_service
from schema.request.auth_schemas import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
)
from schema.response.auth_schemas import LoginResponse, RefreshTokenResponse

router = APIRouter()
security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
def login(
    login_data: LoginRequest, db: Session = Depends(get_db_session)
) -> LoginResponse:
    """Login user and return access and refresh tokens"""
    try:
        result = auth_service.login(db, login_data.email, login_data.password)
        return LoginResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/register")
def register(
    register_data: RegisterRequest, db: Session = Depends(get_db_session)
) -> Dict[str, str]:
    """Register a new user (for testing purposes)"""
    try:
        from model.user.users import User

        # Check if user already exists
        existing_user = db.query(User).filter(User.email == register_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Hash password
        hashed_password = auth_service.get_password_hash(register_data.password)

        # Create new user
        new_user = User(
            email=register_data.email,
            password=hashed_password,
            first_name=register_data.first_name,
            last_name=register_data.last_name,
            birth_date=register_data.birth_date,
            role_id=register_data.role_id or 1,
            is_active=True,
        )

        db.add(new_user)
        db.commit()

        return {"message": "User registered successfully", "user_id": str(new_user.id)}

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}",
        )


@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_token(
    refresh_data: RefreshTokenRequest, db: Session = Depends(get_db_session)
) -> RefreshTokenResponse:
    """Refresh access token using refresh token"""
    try:
        result = auth_service.refresh_access_token(db, refresh_data.refresh_token)
        return RefreshTokenResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session),
) -> Dict[str, str]:
    """Logout user by blacklisting their tokens"""
    try:
        auth_service.logout(db, credentials.credentials)
        return {"message": "Successfully logged out"}
    except Exception as e:
        # For authentication-related errors, return 401 instead of 500
        error_msg = str(e).lower()
        if any(
            keyword in error_msg
            for keyword in ["jwt", "token", "signature", "decode", "invalid"]
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Logout failed: {str(e)}",
            )


@router.get("/me")
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db_session),
) -> Dict[str, Any]:
    """Get current user information"""
    try:
        payload = auth_service.verify_token(db, credentials.credentials, "access")
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        from model.user.users import User

        user_id = int(payload.get("sub"))
        user = db.query(User).filter(User.id == user_id).first()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role_id": user.role_id,
            "is_active": user.is_active,
        }
    except HTTPException:
        raise
    except Exception as e:
        # For authentication-related errors, return 401 instead of 500
        error_msg = str(e).lower()
        if any(
            keyword in error_msg
            for keyword in ["jwt", "token", "signature", "decode", "invalid"]
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user info: {str(e)}",
            )
