from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from model.master.user_roles import UserRole as Role
from services.base_service import BaseService
from schema.request.role_schemas import RoleCreateRequest, RoleUpdateRequest
from core.common.exceptions import HRSystemBaseException
from starlette import status


class RoleService(BaseService[Role]):
    def __init__(self):
        super().__init__(Role)

    def create_role(self, db: Session, role_data: RoleCreateRequest) -> Role:
        """Create a new role with validation"""
        # Check if name already exists
        existing_role = self.get_by_field(db, "name", role_data.name)
        if existing_role:
            raise HRSystemBaseException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Role name already exists"
            )
        
        role_dict = role_data.model_dump()
        return self.create(db, role_dict)

    def update_role(self, db: Session, role_id: int, role_data: RoleUpdateRequest) -> Optional[Role]:
        """Update role with validation"""
        # Check if name already exists for another role
        if role_data.name:
            existing_role = db.query(Role).filter(
                and_(
                    Role.name == role_data.name,
                    Role.id != role_id,
                    Role.deleted_at.is_(None)
                )
            ).first()
            if existing_role:
                raise HRSystemBaseException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Role name already exists"
                )
        
        role_dict = role_data.model_dump(exclude_unset=True)
        return self.update(db, role_id, role_dict)

    def get_role_by_name(self, db: Session, name: str) -> Optional[Role]:
        """Get role by name"""
        return self.get_by_field(db, "name", name)

    def get_active_roles(self, db: Session) -> List[Role]:
        """Get all active roles"""
        return db.query(Role).filter(
            and_(
                Role.is_active == True,
                Role.deleted_at.is_(None)
            )
        ).all()

    def activate_role(self, db: Session, role_id: int) -> Optional[Role]:
        """Activate a role"""
        return self.update(db, role_id, {"is_active": True})

    def deactivate_role(self, db: Session, role_id: int) -> Optional[Role]:
        """Deactivate a role"""
        return self.update(db, role_id, {"is_active": False})


# Create singleton instance
role_service = RoleService()
