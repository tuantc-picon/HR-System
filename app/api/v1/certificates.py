from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.common.database import get_db_session
from services.certificate_service import certificate_service
from schema.request.certificate_schemas import (
    CertificateCreateRequest,
    CertificateUpdateRequest,
)
from schema.response.certificate_schemas import CertificateResponse
from core.common.exceptions import HRSystemBaseException

router = APIRouter()


@router.post(
    "/", response_model=CertificateResponse, status_code=status.HTTP_201_CREATED
)
def create_certificate(
    certificate_data: CertificateCreateRequest, db: Session = Depends(get_db_session)
):
    """Create a new certificate"""
    try:
        certificate = certificate_service.create_certificate(db, certificate_data)
        return certificate
    except HRSystemBaseException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.get("/", response_model=List[CertificateResponse])
def get_certificates(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db_session)
):
    """Get all certificates"""
    certificates = certificate_service.get_all(db, skip=skip, limit=limit)
    return certificates


@router.get("/{certificate_id}", response_model=CertificateResponse)
def get_certificate(certificate_id: int, db: Session = Depends(get_db_session)):
    """Get certificate by ID"""
    certificate = certificate_service.get_by_id(db, certificate_id)
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found"
        )
    return certificate


@router.put("/{certificate_id}", response_model=CertificateResponse)
def update_certificate(
    certificate_id: int,
    certificate_data: CertificateUpdateRequest,
    db: Session = Depends(get_db_session),
):
    """Update certificate"""
    try:
        certificate = certificate_service.update_certificate(
            db, certificate_id, certificate_data
        )
        if not certificate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found"
            )
        return certificate
    except HRSystemBaseException as e:
        raise HTTPException(status_code=e.code, detail=e.message)


@router.delete("/{certificate_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_certificate(certificate_id: int, db: Session = Depends(get_db_session)):
    """Soft delete certificate"""
    success = certificate_service.soft_delete(db, certificate_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found"
        )


@router.get("/name/{name}", response_model=CertificateResponse)
def get_certificate_by_name(name: str, db: Session = Depends(get_db_session)):
    """Get certificate by name"""
    certificate = certificate_service.get_certificate_by_name(db, name)
    if not certificate:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Certificate not found"
        )
    return certificate


@router.get("/active/list", response_model=List[CertificateResponse])
def get_active_certificates(db: Session = Depends(get_db_session)):
    """Get all active certificates"""
    certificates = certificate_service.get_active_certificates(db)
    return certificates


@router.get("/category/{category}", response_model=List[CertificateResponse])
def get_certificates_by_category(category: int, db: Session = Depends(get_db_session)):
    """Get certificates by category"""
    certificates = certificate_service.get_certificates_by_category(db, category)
    return certificates
