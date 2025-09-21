from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from model.master.skills import Skill
from services.base_service import BaseService
from schema.request.skill_schemas import SkillCreateRequest, SkillUpdateRequest
from core.common.exceptions import HRSystemBaseException
from starlette import status


class SkillService(BaseService[Skill]):
    def __init__(self):
        super().__init__(Skill)

    def create_skill(self, db: Session, skill_data: SkillCreateRequest) -> Skill:
        """Create a new skill with validation"""
        # Check if skill name already exists
        existing_skill = self.get_by_field(db, "name", skill_data.name)
        if existing_skill:
            raise HRSystemBaseException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Skill name already exists",
            )

        skill_dict = skill_data.model_dump()
        return self.create(db, skill_dict)

    def update_skill(
        self, db: Session, skill_id: int, skill_data: SkillUpdateRequest
    ) -> Optional[Skill]:
        """Update skill with validation"""
        # If name is being updated, check for duplicates
        if skill_data.name:
            existing_skill = self.get_by_field(db, "name", skill_data.name)
            if existing_skill and existing_skill.id != skill_id:
                raise HRSystemBaseException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Skill name already exists",
                )

        skill_dict = skill_data.model_dump(exclude_unset=True)
        return self.update(db, skill_id, skill_dict)

    def get_active_skills(self, db: Session) -> List[Skill]:
        """Get all active skills"""
        return (
            db.query(Skill)
            .filter(and_(Skill.is_active == True, Skill.deleted_at.is_(None)))
            .all()
        )

    def activate_skill(self, db: Session, skill_id: int) -> Optional[Skill]:
        """Activate a skill"""
        skill = self.get_by_id(db, skill_id)
        if not skill:
            return None

        skill.is_active = True
        db.commit()
        db.refresh(skill)
        return skill

    def deactivate_skill(self, db: Session, skill_id: int) -> Optional[Skill]:
        """Deactivate a skill"""
        skill = self.get_by_id(db, skill_id)
        if not skill:
            return None

        skill.is_active = False
        db.commit()
        db.refresh(skill)
        return skill

    def search_skills_by_name(self, db: Session, name: str) -> List[Skill]:
        """Search skills by name (case-insensitive)"""
        return (
            db.query(Skill)
            .filter(and_(Skill.name.ilike(f"%{name}%"), Skill.deleted_at.is_(None)))
            .all()
        )


# Create singleton instance
skill_service = SkillService()
