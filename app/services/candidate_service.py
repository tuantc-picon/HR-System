from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from fastapi import UploadFile

from model.candidate.candidates import Candidate
from model.candidate.resumes import Resume
from services.base_service import BaseService
from services.file_upload_service import file_upload_service
from services.resume_service import resume_service
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

    async def create_candidate_with_cv(
        self,
        db: Session,
        candidate_data: CandidateCreateRequest,
        cv_file: Optional[UploadFile] = None
    ) -> Dict[str, Any]:
        """
        Create a new candidate with optional CV upload

        Args:
            db: Database session
            candidate_data: Candidate information
            cv_file: Optional CV file upload

        Returns:
            Dict containing candidate, resume (if uploaded), and upload info
        """
        # Check if email already exists
        existing_candidate = self.get_by_field(db, "email", candidate_data.email)
        if existing_candidate:
            raise HRSystemBaseException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Email already exists"
            )

        # Validate CV file type before creating candidate
        if cv_file and cv_file.filename:
            if not cv_file.filename.lower().endswith('.pdf'):
                raise HRSystemBaseException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Only PDF files are allowed for CV upload"
                )

        # Create candidate
        candidate_dict = candidate_data.model_dump()
        candidate = self.create(db, candidate_dict)

        result = {
            "candidate": candidate,
            "resume": None,
            "upload_info": None
        }

        # Handle CV upload if provided
        if cv_file and cv_file.filename:
            try:

                # Upload file
                upload_result = await file_upload_service.upload_file(cv_file, "resumes")

                if upload_result["success"]:
                    # Create resume record
                    resume_data = {
                        "candidate_id": candidate.id,
                        "file_path": upload_result["file_path"],
                        "note": f"CV uploaded on candidate creation - {upload_result['original_filename']}"
                    }

                    resume = resume_service.create(db, resume_data)
                    result["resume"] = resume
                    result["upload_info"] = upload_result
                else:
                    # If file upload fails, we could either:
                    # 1. Delete the candidate and raise an error
                    # 2. Keep the candidate and return the error info
                    # Let's keep the candidate and return the error info
                    result["upload_info"] = upload_result

            except Exception as e:
                # Log the error but don't fail candidate creation
                result["upload_info"] = {
                    "success": False,
                    "error": str(e),
                    "storage_type": "unknown"
                }

        return result

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

    def get_candidate_with_resumes(self, db: Session, candidate_id: int) -> Optional[Candidate]:
        """Get candidate with their resumes"""
        candidate = self.get_by_id(db, candidate_id)
        if candidate:
            # Get resumes for this candidate
            resumes = resume_service.get_resumes_by_candidate(db, candidate_id)
            # Add resumes to candidate object (this will be handled by the response model)
            candidate.resumes = resumes
        return candidate


# Create singleton instance
candidate_service = CandidateService()
