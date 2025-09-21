from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from model.job.job_requirement_certificates import JobRequirementCertificate
from services.base_service import BaseService
from schema.request.job_requirement_certificate_schemas import (
    JobRequirementCertificateCreateRequest,
    JobRequirementCertificateUpdateRequest,
)
from core.common.exceptions import HRSystemBaseException
from starlette import status


class JobRequirementCertificateService(BaseService[JobRequirementCertificate]):
    def __init__(self):
        super().__init__(JobRequirementCertificate)

    def create_job_requirement_certificate(
        self, db: Session, data: JobRequirementCertificateCreateRequest
    ) -> JobRequirementCertificate:
        """Create a new job requirement certificate association with validation"""
        # Check if association already exists
        existing_association = (
            db.query(JobRequirementCertificate)
            .filter(
                and_(
                    JobRequirementCertificate.job_requirement_id
                    == data.job_requirement_id,
                    JobRequirementCertificate.certificate_id == data.certificate_id,
                    JobRequirementCertificate.deleted_at.is_(None),
                )
            )
            .first()
        )

        if existing_association:
            raise HRSystemBaseException(
                status_code=status.HTTP_400_BAD_REQUEST,
                message="This certificate is already associated with the job requirement",
            )

        association_dict = data.model_dump()
        return self.create(db, association_dict)

    def update_job_requirement_certificate(
        self,
        db: Session,
        association_id: int,
        data: JobRequirementCertificateUpdateRequest,
    ) -> Optional[JobRequirementCertificate]:
        """Update job requirement certificate association"""
        association_dict = data.model_dump(exclude_unset=True)
        return self.update(db, association_id, association_dict)

    def get_certificates_by_job_requirement(
        self, db: Session, job_requirement_id: int
    ) -> List[JobRequirementCertificate]:
        """Get all certificates for a specific job requirement"""
        return (
            db.query(JobRequirementCertificate)
            .filter(
                and_(
                    JobRequirementCertificate.job_requirement_id == job_requirement_id,
                    JobRequirementCertificate.deleted_at.is_(None),
                )
            )
            .all()
        )

    def get_job_requirements_by_certificate(
        self, db: Session, certificate_id: int
    ) -> List[JobRequirementCertificate]:
        """Get all job requirements that require a specific certificate"""
        return (
            db.query(JobRequirementCertificate)
            .filter(
                and_(
                    JobRequirementCertificate.certificate_id == certificate_id,
                    JobRequirementCertificate.deleted_at.is_(None),
                )
            )
            .all()
        )

    def remove_certificate_from_job_requirement(
        self, db: Session, job_requirement_id: int, certificate_id: int
    ) -> bool:
        """Remove a certificate from a job requirement"""
        association = (
            db.query(JobRequirementCertificate)
            .filter(
                and_(
                    JobRequirementCertificate.job_requirement_id == job_requirement_id,
                    JobRequirementCertificate.certificate_id == certificate_id,
                    JobRequirementCertificate.deleted_at.is_(None),
                )
            )
            .first()
        )

        if association:
            return self.soft_delete(db, association.id)
        return False


# Create singleton instance
job_requirement_certificate_service = JobRequirementCertificateService()
