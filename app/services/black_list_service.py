from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from model.master.black_lists import BlackList
from services.base_service import BaseService
from schema.request.black_list_schemas import (
    BlackListCreateRequest,
    BlackListUpdateRequest,
)
from core.common.exceptions import HRSystemBaseException
from starlette import status


class BlackListService(BaseService[BlackList]):
    def __init__(self):
        super().__init__(BlackList)

    def create_black_list(
        self, db: Session, black_list_data: BlackListCreateRequest
    ) -> BlackList:
        """Create a new black list entry with validation"""
        # Check if name already exists
        existing_black_list = self.get_by_field(db, "name", black_list_data.name)
        if existing_black_list:
            raise HRSystemBaseException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Black list name already exists",
            )

        black_list_dict = black_list_data.model_dump()
        return self.create(db, black_list_dict)

    def update_black_list(
        self, db: Session, black_list_id: int, black_list_data: BlackListUpdateRequest
    ) -> Optional[BlackList]:
        """Update black list with validation"""
        # Check if name already exists for another black list entry
        if black_list_data.name:
            existing_black_list = (
                db.query(BlackList)
                .filter(
                    and_(
                        BlackList.name == black_list_data.name,
                        BlackList.id != black_list_id,
                        BlackList.deleted_at.is_(None),
                    )
                )
                .first()
            )
            if existing_black_list:
                raise HRSystemBaseException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Black list name already exists",
                )

        black_list_dict = black_list_data.model_dump(exclude_unset=True)
        return self.update(db, black_list_id, black_list_dict)

    def get_black_list_by_name(self, db: Session, name: str) -> Optional[BlackList]:
        """Get black list by name"""
        return self.get_by_field(db, "name", name)

    def get_active_black_lists(self, db: Session) -> List[BlackList]:
        """Get all active black list entries"""
        return (
            db.query(BlackList)
            .filter(and_(BlackList.is_active == True, BlackList.deleted_at.is_(None)))
            .all()
        )

    def get_black_lists_by_category(
        self, db: Session, category: int
    ) -> List[BlackList]:
        """Get black lists by category (1: Candidate, 3: Company)"""
        return (
            db.query(BlackList)
            .filter(
                and_(BlackList.category == category, BlackList.deleted_at.is_(None))
            )
            .all()
        )


# Create singleton instance
black_list_service = BlackListService()
