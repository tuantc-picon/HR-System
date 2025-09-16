from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.common.database import get_db_session
from services.skill_service import skill_service
from schema.request.skill_schemas import SkillCreateRequest, SkillUpdateRequest
from schema.response.skill_schemas import SkillResponse

router = APIRouter()


@router.post("/", response_model=SkillResponse, status_code=status.HTTP_201_CREATED)
def create_skill(
    skill_data: SkillCreateRequest,
    db: Session = Depends(get_db_session)
):
    """Create a new skill"""
    skill = skill_service.create_skill(db, skill_data)
    return skill


@router.get("/", response_model=List[SkillResponse])
def get_skills(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session)
):
    """Get all skills"""
    skills = skill_service.get_all(db, skip=skip, limit=limit)
    return skills


@router.get("/active/list", response_model=List[SkillResponse])
def get_active_skills(
    db: Session = Depends(get_db_session)
):
    """Get all active skills"""
    skills = skill_service.get_active_skills(db)
    return skills


@router.get("/{skill_id}", response_model=SkillResponse)
def get_skill(
    skill_id: int,
    db: Session = Depends(get_db_session)
):
    """Get skill by ID"""
    skill = skill_service.get_by_id(db, skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    return skill


@router.put("/{skill_id}", response_model=SkillResponse)
def update_skill(
    skill_id: int,
    skill_data: SkillUpdateRequest,
    db: Session = Depends(get_db_session)
):
    """Update skill"""
    skill = skill_service.update_skill(db, skill_id, skill_data)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    return skill


@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_skill(
    skill_id: int,
    db: Session = Depends(get_db_session)
):
    """Soft delete skill"""
    success = skill_service.soft_delete(db, skill_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )


@router.put("/{skill_id}/activate", response_model=SkillResponse)
def activate_skill(
    skill_id: int,
    db: Session = Depends(get_db_session)
):
    """Activate skill"""
    skill = skill_service.activate_skill(db, skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    return skill


@router.put("/{skill_id}/deactivate", response_model=SkillResponse)
def deactivate_skill(
    skill_id: int,
    db: Session = Depends(get_db_session)
):
    """Deactivate skill"""
    skill = skill_service.deactivate_skill(db, skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found"
        )
    return skill


@router.get("/name/{name}", response_model=List[SkillResponse])
def search_skills_by_name(
    name: str,
    db: Session = Depends(get_db_session)
):
    """Search skills by name"""
    skills = skill_service.search_skills_by_name(db, name)
    return skills
