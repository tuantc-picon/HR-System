import os
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from fastapi import HTTPException, status
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import and_

from config import BASE_DIR, UPLOAD_CLOUD_TARGET
from model.candidate.resumes import Resume
from model.application.applications import Application
from model.candidate.candidates import Candidate
from model.job.jobs import Job
from model.user.users import User
from services.file_upload_service import file_upload_service


class FileService:
    """
    Service for handling file serving with proper security and access control
    """

    def __init__(self):
        self.upload_dir = BASE_DIR / "uploads"
        self.allowed_extensions = {
            ".pdf",
            ".doc",
            ".docx",
            ".txt",
            ".rtf",
            ".odt",
            ".pages",
            ".jpg",
            ".jpeg",
            ".png",
        }
        self.max_file_size = 50 * 1024 * 1024  # 50MB

    def _get_mime_type(self, file_path: str) -> str:
        """Get MIME type for file"""
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            return mime_type

        # Default MIME types for common resume formats
        extension = Path(file_path).suffix.lower()
        mime_types = {
            ".pdf": "application/pdf",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            ".txt": "text/plain",
            ".rtf": "application/rtf",
            ".odt": "application/vnd.oasis.opendocument.text",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
        }
        return mime_types.get(extension, "application/octet-stream")

    def _validate_file_extension(self, file_path: str) -> bool:
        """Validate file extension"""
        extension = Path(file_path).suffix.lower()
        return extension in self.allowed_extensions

    def _check_file_access_permission(
        self, db: Session, resume_id: int, user: User
    ) -> bool:
        """
        Check if user has permission to access the resume file
        Rules:
        1. HR users (role_id = 1) can access all resumes
        2. Managers (role_id = 2) can access resumes for jobs they created
        3. Users can access resumes if they are associated with candidates they manage
        4. For now, authenticated users can access resumes (can be restricted later)
        """
        try:
            # Get the resume
            resume = (
                db.query(Resume)
                .filter(and_(Resume.id == resume_id, Resume.deleted_at.is_(None)))
                .first()
            )

            if not resume:
                return False

            # HR users (role_id = 1) can access all files
            if user.role_id == 1:
                return True

            # Check if user is a manager who created jobs that have applications with this resume
            if user.role_id == 2:  # Manager role
                manager_job_application = (
                    db.query(Application)
                    .join(Job, Application.job_id == Job.id)
                    .filter(
                        and_(
                            Application.resume_id == resume_id,
                            Job.created_by == user.id,
                            Application.deleted_at.is_(None),
                            Job.deleted_at.is_(None),
                        )
                    )
                    .first()
                )

                if manager_job_application:
                    return True

            # Check if there are any applications using this resume
            # (For now, allow access if the resume is used in any application)
            # This can be made more restrictive based on business requirements
            application_exists = (
                db.query(Application)
                .filter(
                    and_(
                        Application.resume_id == resume_id,
                        Application.deleted_at.is_(None),
                    )
                )
                .first()
            )

            if application_exists:
                return True

            # For now, allow authenticated users to access resumes
            # This can be made more restrictive based on business requirements
            return True

        except Exception:
            return False

    def _get_resume_by_file_path(self, db: Session, file_path: str) -> Optional[Resume]:
        """Get resume by file path - handle different path formats"""
        # Try exact match first
        resume = (
            db.query(Resume)
            .filter(and_(Resume.file_path == file_path, Resume.deleted_at.is_(None)))
            .first()
        )

        if resume:
            return resume

        # If not found, try different path variations
        # Handle case where input has /uploads/ but database doesn't
        if file_path.startswith("/uploads/"):
            alt_path = file_path[9:]  # Remove '/uploads/'
            resume = (
                db.query(Resume)
                .filter(and_(Resume.file_path == alt_path, Resume.deleted_at.is_(None)))
                .first()
            )
            if resume:
                return resume

        # Handle case where input doesn't have /uploads/ but database does
        elif not file_path.startswith("/uploads/") and not file_path.startswith("http"):
            alt_path = f"/uploads/{file_path}"
            resume = (
                db.query(Resume)
                .filter(and_(Resume.file_path == alt_path, Resume.deleted_at.is_(None)))
                .first()
            )
            if resume:
                return resume

        return None

    def serve_resume_file(
        self, db: Session, file_path: str, user: User
    ) -> Tuple[Any, Dict[str, str]]:
        """
        Serve resume file with proper access control

        Returns:
            Tuple of (response, headers)
        """
        try:
            # Get resume by file path
            resume = self._get_resume_by_file_path(db, file_path)

            if not resume:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Resume file not found for path: {file_path}",
                )

            # Check access permission
            if not self._check_file_access_permission(db, resume.id, user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You don't have permission to access this file",
                )

            # Validate file extension
            if not self._validate_file_extension(file_path):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="File type not supported",
                )

            # Determine storage type and handle accordingly
            if file_path.startswith("http"):
                # Google Drive file - redirect to the URL
                return self._serve_google_drive_file(file_path)
            else:
                # Local file - serve from local storage
                return self._serve_local_file(file_path)

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error serving file: {str(e)}",
            )

    def _serve_local_file(self, file_path: str) -> Tuple[FileResponse, Dict[str, str]]:
        """Serve local file"""
        # Normalize file path - handle different formats stored in database
        normalized_path = file_path

        # Remove leading /uploads/ if present (for newer format)
        if normalized_path.startswith("/uploads/"):
            normalized_path = normalized_path[9:]  # Remove '/uploads/'

        # Remove leading uploads/ if present (for some edge cases)
        elif normalized_path.startswith("uploads/"):
            normalized_path = normalized_path[8:]  # Remove 'uploads/'

        # Construct full file path
        full_path = self.upload_dir / normalized_path

        # Security check: ensure file is within upload directory
        try:
            full_path = full_path.resolve()
            upload_dir_resolved = self.upload_dir.resolve()

            if not str(full_path).startswith(str(upload_dir_resolved)):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: Invalid file path",
                )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Invalid file path",
            )

        # Check if file exists
        if not full_path.exists() or not full_path.is_file():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="File not found on server"
            )

        # Check file size
        if full_path.stat().st_size > self.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large",
            )

        # Get MIME type and filename
        mime_type = self._get_mime_type(str(full_path))
        filename = full_path.name

        # Prepare headers
        headers = {
            "Content-Type": mime_type,
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "private, max-age=3600",  # Cache for 1 hour
        }

        return (
            FileResponse(
                path=str(full_path),
                media_type=mime_type,
                filename=filename,
                headers=headers,
            ),
            headers,
        )

    def _serve_google_drive_file(
        self, file_url: str
    ) -> Tuple[RedirectResponse, Dict[str, str]]:
        """Serve Google Drive file by redirecting to the URL"""
        # For Google Drive files, we redirect to the file URL
        # In a production environment, you might want to proxy the file
        # or use Google Drive API to get a temporary download link

        headers = {
            "Cache-Control": "private, max-age=300",  # Cache for 5 minutes
        }

        # Convert view link to download link if needed
        if "drive.google.com/file/d/" in file_url and "/view" in file_url:
            # Extract file ID and create direct download link
            file_id = file_url.split("/file/d/")[1].split("/")[0]
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        else:
            download_url = file_url

        return (
            RedirectResponse(
                url=download_url, status_code=status.HTTP_302_FOUND, headers=headers
            ),
            headers,
        )

    def get_file_info(self, db: Session, file_path: str, user: User) -> Dict[str, Any]:
        """Get file information without serving the file"""
        try:
            # Get resume by file path
            resume = self._get_resume_by_file_path(db, file_path)
            if not resume:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Resume file not found",
                )

            # Check access permission
            if not self._check_file_access_permission(db, resume.id, user):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: You don't have permission to access this file",
                )

            # Determine storage type
            storage_type = "google_drive" if file_path.startswith("http") else "local"

            file_info = {
                "resume_id": resume.id,
                "candidate_id": resume.candidate_id,
                "file_path": file_path,
                "storage_type": storage_type,
                "mime_type": self._get_mime_type(file_path),
                "note": resume.note,
                "created_at": resume.created_at.isoformat(),
            }

            # Add file size for local files
            if storage_type == "local":
                full_path = self.upload_dir / file_path.lstrip("/uploads/")
                if full_path.exists():
                    file_info["file_size"] = full_path.stat().st_size

            return file_info

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting file info: {str(e)}",
            )


# Create singleton instance
file_service = FileService()
