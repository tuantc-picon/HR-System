from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.common.database import get_db_session
from services.role_service import role_service
from schema.request.role_schemas import RoleCreateRequest, RoleUpdateRequest
from schema.response.role_schemas import RoleResponse
from core.common.exceptions import HRSystemBaseException

router = APIRouter()


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def create_role(
    role_data: RoleCreateRequest,
    db: Session = Depends(get_db_session)
):
    """Create a new role"""
    try:
        role = role_service.create_role(db, role_data)
        return role
    except HRSystemBaseException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/", response_model=List[RoleResponse])
def get_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session)
):
    """Get all roles"""
    roles = role_service.get_all(db, skip=skip, limit=limit)
    return roles


@router.get("/{role_id}", response_model=RoleResponse)
def get_role(
    role_id: int,
    db: Session = Depends(get_db_session)
):
    """Get role by ID"""
    role = role_service.get_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role


@router.put("/{role_id}", response_model=RoleResponse)
def update_role(
    role_id: int,
    role_data: RoleUpdateRequest,
    db: Session = Depends(get_db_session)
):
    """Update role"""
    try:
        role = role_service.update_role(db, role_id, role_data)
        if not role:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found"
            )
        return role
    except HRSystemBaseException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: int,
    db: Session = Depends(get_db_session)
):
    """Soft delete role"""
    success = role_service.soft_delete(db, role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )


@router.get("/name/{name}", response_model=RoleResponse)
def get_role_by_name(
    name: str,
    db: Session = Depends(get_db_session)
):
    """Get role by name"""
    role = role_service.get_role_by_name(db, name)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role


@router.get("/active/list", response_model=List[RoleResponse])
def get_active_roles(
    db: Session = Depends(get_db_session)
):
    """Get all active roles"""
    roles = role_service.get_active_roles(db)
    return roles


@router.patch("/{role_id}/activate", response_model=RoleResponse)
def activate_role(
    role_id: int,
    db: Session = Depends(get_db_session)
):
    """Activate role"""
    role = role_service.activate_role(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role


@router.patch("/{role_id}/deactivate", response_model=RoleResponse)
def deactivate_role(
    role_id: int,
    db: Session = Depends(get_db_session)
):
    """Deactivate role"""
    role = role_service.deactivate_role(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role
