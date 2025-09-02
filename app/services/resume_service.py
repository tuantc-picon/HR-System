from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from model.candidate.resumes import Resume
from services.base_service import BaseService
from schema.request.resume_schemas import ResumeCreateRequest, ResumeUpdateRequest


class ResumeService(BaseService[Resume]):
    def __init__(self):
        super().__init__(Resume)

    def create_resume(self, db: Session, resume_data: ResumeCreateRequest) -> Resume:
        """Create a new resume"""
        resume_dict = resume_data.model_dump()
        return self.create(db, resume_dict)

    def update_resume(self, db: Session, resume_id: int, resume_data: ResumeUpdateRequest) -> Optional[Resume]:
        """Update resume"""
        resume_dict = resume_data.model_dump(exclude_unset=True)
        return self.update(db, resume_id, resume_dict)

    def get_resumes_by_candidate(self, db: Session, candidate_id: int) -> List[Resume]:
        """Get all resumes for a specific candidate"""
        return db.query(Resume).filter(
            and_(
                Resume.candidate_id == candidate_id,
                Resume.deleted_at.is_(None)
            )
        ).all()

    def get_resume_by_file_path(self, db: Session, file_path: str) -> Optional[Resume]:
        """Get resume by file path"""
        return self.get_by_field(db, "file_path", file_path)


# Create singleton instance
resume_service = ResumeService()
