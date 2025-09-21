from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from model.user.users import User
from services.base_service import BaseService
from schema.request.user_schemas import UserCreateRequest, UserUpdateRequest
from core.common.exceptions import HRSystemBaseException
from starlette import status


class UserService(BaseService[User]):
    def __init__(self):
        super().__init__(User)

    def create_user(self, db: Session, user_data: UserCreateRequest) -> User:
        """Create a new user with validation"""
        # Check if email already exists
        existing_user = self.get_by_field(db, "email", user_data.email)
        if existing_user:
            raise HRSystemBaseException(
                status_code=status.HTTP_400_BAD_REQUEST, message="Email already exists"
            )

        user_dict = user_data.model_dump()
        return self.create(db, user_dict)

    def update_user(
        self, db: Session, user_id: int, user_data: UserUpdateRequest
    ) -> Optional[User]:
        """Update user with validation"""
        # Check if email already exists for another user
        if user_data.email:
            existing_user = (
                db.query(User)
                .filter(
                    and_(
                        User.email == user_data.email,
                        User.id != user_id,
                        User.deleted_at.is_(None),
                    )
                )
                .first()
            )
            if existing_user:
                raise HRSystemBaseException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Email already exists",
                )

        user_dict = user_data.model_dump(exclude_unset=True)
        return self.update(db, user_id, user_dict)

    def get_user_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return self.get_by_field(db, "email", email)

    def get_users_by_role(self, db: Session, role_id: int) -> List[User]:
        """Get all users by role ID"""
        return (
            db.query(User)
            .filter(and_(User.role_id == role_id, User.deleted_at.is_(None)))
            .all()
        )

    def activate_user(self, db: Session, user_id: int) -> Optional[User]:
        """Activate a user"""
        return self.update(db, user_id, {"is_active": True})

    def deactivate_user(self, db: Session, user_id: int) -> Optional[User]:
        """Deactivate a user"""
        return self.update(db, user_id, {"is_active": False})


# Create singleton instance
user_service = UserService()
