from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from model.candidate.candidates import Candidate
from services.base_service import BaseService
from schema.request.candidate_schemas import CandidateCreateRequest, CandidateUpdateRequest
from core.common.exceptions import HRSystemBaseException
from starlette import status


class CandidateService(BaseService[Candidate]):
    def __init__(self):
        super().__init__(Candidate)

    def create_candidate(self, db: Session, candidate_data: CandidateCreateRequest) -> Candidate:
        """Create a new candidate with validation"""
        # Check if email already exists
        existing_candidate = self.get_by_field(db, "email", candidate_data.email)
        if existing_candidate:
            raise HRSystemBaseException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Email already exists"
            )
        
        candidate_dict = candidate_data.model_dump()
        return self.create(db, candidate_dict)

    def update_candidate(self, db: Session, candidate_id: int, candidate_data: CandidateUpdateRequest) -> Optional[Candidate]:
        """Update candidate with validation"""
        # Check if email already exists for another candidate
        if candidate_data.email:
            existing_candidate = db.query(Candidate).filter(
                and_(
                    Candidate.email == candidate_data.email,
                    Candidate.id != candidate_id,
                    Candidate.deleted_at.is_(None)
                )
            ).first()
            if existing_candidate:
                raise HRSystemBaseException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Email already exists"
                )
        
        candidate_dict = candidate_data.model_dump(exclude_unset=True)
        return self.update(db, candidate_id, candidate_dict)

    def get_candidate_by_email(self, db: Session, email: str) -> Optional[Candidate]:
        """Get candidate by email"""
        return self.get_by_field(db, "email", email)

    def search_candidates_by_name(self, db: Session, name_keyword: str) -> List[Candidate]:
        """Search candidates by first name or last name"""
        return db.query(Candidate).filter(
            and_(
                (Candidate.first_name.ilike(f"%{name_keyword}%") | 
                 Candidate.last_name.ilike(f"%{name_keyword}%")),
                Candidate.deleted_at.is_(None)
            )
        ).all()

    def get_candidates_by_phone(self, db: Session, phone_number: str) -> Optional[Candidate]:
        """Get candidate by phone number"""
        return self.get_by_field(db, "phone_number", phone_number)


# Create singleton instance
candidate_service = CandidateService()
