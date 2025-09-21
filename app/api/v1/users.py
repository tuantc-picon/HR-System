from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.common.database import get_db_session
from core.middleware.auth_middleware import get_current_active_user
from model.user.users import User
from services.user_service import user_service
from schema.request.user_schemas import UserCreateRequest, UserUpdateRequest
from schema.response.user_schemas import UserResponse
from core.common.exceptions import HRSystemBaseException

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreateRequest,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new user"""
    try:
        user = user_service.create_user(db, user_data)
        return user
    except HRSystemBaseException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)):
    """Get all users"""
    users = user_service.get_all(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db_session)):
    """Get user by ID"""
    user = user_service.get_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, user_data: UserUpdateRequest, db: Session = Depends(get_db_session)
):
    """Update user"""
    try:
        user = user_service.update_user(db, user_id, user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )
        return user
    except HRSystemBaseException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db_session)):
    """Soft delete user"""
    success = user_service.soft_delete(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )


@router.get("/email/{email}", response_model=UserResponse)
def get_user_by_email(email: str, db: Session = Depends(get_db_session)):
    """Get user by email"""
    user = user_service.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.get("/role/{role_id}", response_model=List[UserResponse])
def get_users_by_role(role_id: int, db: Session = Depends(get_db_session)):
    """Get users by role"""
    users = user_service.get_users_by_role(db, role_id)
    return users


@router.patch("/{user_id}/activate", response_model=UserResponse)
def activate_user(user_id: int, db: Session = Depends(get_db_session)):
    """Activate user"""
    user = user_service.activate_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


@router.patch("/{user_id}/deactivate", response_model=UserResponse)
def deactivate_user(user_id: int, db: Session = Depends(get_db_session)):
    """Deactivate user"""
    user = user_service.deactivate_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
