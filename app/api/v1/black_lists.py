from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.common.database import get_db_session
from services.black_list_service import black_list_service
from schema.request.black_list_schemas import BlackListCreateRequest, BlackListUpdateRequest
from schema.response.black_list_schemas import BlackListResponse
from core.common.exceptions import HRSystemBaseException

router = APIRouter()


@router.post("/", response_model=BlackListResponse, status_code=status.HTTP_201_CREATED)
def create_black_list(
    black_list_data: BlackListCreateRequest,
    db: Session = Depends(get_db_session)
):
    """Create a new black list entry"""
    try:
        black_list = black_list_service.create_black_list(db, black_list_data)
        return black_list
    except HRSystemBaseException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/", response_model=List[BlackListResponse])
def get_black_lists(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session)
):
    """Get all black list entries"""
    black_lists = black_list_service.get_all(db, skip=skip, limit=limit)
    return black_lists


@router.get("/{black_list_id}", response_model=BlackListResponse)
def get_black_list(
    black_list_id: int,
    db: Session = Depends(get_db_session)
):
    """Get black list entry by ID"""
    black_list = black_list_service.get_by_id(db, black_list_id)
    if not black_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Black list entry not found"
        )
    return black_list


@router.put("/{black_list_id}", response_model=BlackListResponse)
def update_black_list(
    black_list_id: int,
    black_list_data: BlackListUpdateRequest,
    db: Session = Depends(get_db_session)
):
    """Update black list entry"""
    try:
        black_list = black_list_service.update_black_list(db, black_list_id, black_list_data)
        if not black_list:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Black list entry not found"
            )
        return black_list
    except HRSystemBaseException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.delete("/{black_list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_black_list(
    black_list_id: int,
    db: Session = Depends(get_db_session)
):
    """Soft delete black list entry"""
    success = black_list_service.soft_delete(db, black_list_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Black list entry not found"
        )


@router.get("/name/{name}", response_model=BlackListResponse)
def get_black_list_by_name(
    name: str,
    db: Session = Depends(get_db_session)
):
    """Get black list entry by name"""
    black_list = black_list_service.get_black_list_by_name(db, name)
    if not black_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Black list entry not found"
        )
    return black_list


@router.get("/active/list", response_model=List[BlackListResponse])
def get_active_black_lists(
    db: Session = Depends(get_db_session)
):
    """Get all active black list entries"""
    black_lists = black_list_service.get_active_black_lists(db)
    return black_lists


@router.get("/category/{category}", response_model=List[BlackListResponse])
def get_black_lists_by_category(
    category: int,
    db: Session = Depends(get_db_session)
):
    """Get black list entries by category (1: Candidate, 3: Company)"""
    black_lists = black_list_service.get_black_lists_by_category(db, category)
    return black_lists
