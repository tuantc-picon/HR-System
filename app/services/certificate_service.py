from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from model.master.certificates import Certificate
from services.base_service import BaseService
from schema.request.certificate_schemas import CertificateCreateRequest, CertificateUpdateRequest
from core.common.exceptions import HRSystemBaseException
from starlette import status


class CertificateService(BaseService[Certificate]):
    def __init__(self):
        super().__init__(Certificate)

    def create_certificate(self, db: Session, certificate_data: CertificateCreateRequest) -> Certificate:
        """Create a new certificate with validation"""
        # Check if name already exists
        existing_certificate = self.get_by_field(db, "name", certificate_data.name)
        if existing_certificate:
            raise HRSystemBaseException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="Certificate name already exists"
            )
        
        certificate_dict = certificate_data.model_dump()
        return self.create(db, certificate_dict)

    def update_certificate(self, db: Session, certificate_id: int, certificate_data: CertificateUpdateRequest) -> Optional[Certificate]:
        """Update certificate with validation"""
        # Check if name already exists for another certificate
        if certificate_data.name:
            existing_certificate = db.query(Certificate).filter(
                and_(
                    Certificate.name == certificate_data.name,
                    Certificate.id != certificate_id,
                    Certificate.deleted_at.is_(None)
                )
            ).first()
            if existing_certificate:
                raise HRSystemBaseException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    message="Certificate name already exists"
                )
        
        certificate_dict = certificate_data.model_dump(exclude_unset=True)
        return self.update(db, certificate_id, certificate_dict)

    def get_certificate_by_name(self, db: Session, name: str) -> Optional[Certificate]:
        """Get certificate by name"""
        return self.get_by_field(db, "name", name)

    def get_active_certificates(self, db: Session) -> List[Certificate]:
        """Get all active certificates"""
        return db.query(Certificate).filter(
            and_(
                Certificate.is_active == True,
                Certificate.deleted_at.is_(None)
            )
        ).all()

    def get_certificates_by_category(self, db: Session, category: int) -> List[Certificate]:
        """Get certificates by category"""
        return db.query(Certificate).filter(
            and_(
                Certificate.category == category,
                Certificate.deleted_at.is_(None)
            )
        ).all()


# Create singleton instance
certificate_service = CertificateService()
