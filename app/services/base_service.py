from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from model.base import HRSystemBase, utc_now

ModelType = TypeVar("ModelType", bound=HRSystemBase)


class BaseService(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def create(self, db: Session, obj_data: dict) -> ModelType:
        """Create a new record"""
        db_obj = self.model(**obj_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_by_id(self, db: Session, id: int) -> Optional[ModelType]:
        """Get a record by ID (excluding soft deleted)"""
        return db.query(self.model).filter(
            and_(self.model.id == id, self.model.deleted_at.is_(None))
        ).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get all records (excluding soft deleted)"""
        return db.query(self.model).filter(
            self.model.deleted_at.is_(None)
        ).offset(skip).limit(limit).all()

    def update(self, db: Session, id: int, obj_data: dict) -> Optional[ModelType]:
        """Update a record by ID"""
        db_obj = self.get_by_id(db, id)
        if not db_obj:
            return None
        
        for field, value in obj_data.items():
            if value is not None and hasattr(db_obj, field):
                setattr(db_obj, field, value)
        
        db_obj.updated_at = utc_now()
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def soft_delete(self, db: Session, id: int) -> bool:
        """Soft delete a record by setting deleted_at timestamp"""
        db_obj = self.get_by_id(db, id)
        if not db_obj:
            return False
        
        db_obj.deleted_at = utc_now()
        db.commit()
        return True

    def get_by_field(self, db: Session, field_name: str, field_value) -> Optional[ModelType]:
        """Get a record by a specific field (excluding soft deleted)"""
        return db.query(self.model).filter(
            and_(
                getattr(self.model, field_name) == field_value,
                self.model.deleted_at.is_(None)
            )
        ).first()
