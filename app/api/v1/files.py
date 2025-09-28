from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.orm import Session

from core.common.database import get_db_session
from core.middleware.auth_middleware import get_current_active_user
from services.file_service import file_service
from model.user.users import User

router = APIRouter()


@router.get("/resume/{file_path:path}")
def serve_resume_file(
    file_path: str,
    download: bool = Query(
        False, description="Force download instead of inline display"
    ),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session),
):
    """
    Serve resume file with proper access control

    Args:
        file_path: The file path from the resume record
        download: Whether to force download (default: False for inline display)
        current_user: Current authenticated user
        db: Database session

    Returns:
        FileResponse for local files or RedirectResponse for Google Drive files

    Security:
        - Requires authentication
        - Users can only access files they have permission to view
        - HR users can access all files
        - Managers can access files for jobs they created
        - File type validation
        - Path traversal protection
    """
    try:
        response, headers = file_service.serve_resume_file(db, file_path, current_user)

        # Modify Content-Disposition based on download parameter
        if download and "Content-Disposition" in headers:
            # Force download
            headers["Content-Disposition"] = headers["Content-Disposition"].replace(
                "attachment", "attachment"
            )
        elif not download and "Content-Disposition" in headers:
            # Inline display (for PDFs, images, etc.)
            headers["Content-Disposition"] = headers["Content-Disposition"].replace(
                "attachment", "inline"
            )

        # Update headers for FileResponse
        if isinstance(response, FileResponse):
            response.headers.update(headers)

        return response

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error serving file: {str(e)}",
        )


@router.get("/resume-info/{file_path:path}")
def get_resume_file_info(
    file_path: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session),
) -> Dict[str, Any]:
    """
    Get resume file information without downloading the file

    Args:
        file_path: The file path from the resume record
        current_user: Current authenticated user
        db: Database session

    Returns:
        Dict containing file information

    Security:
        - Same access control as file serving
        - Useful for getting file metadata before download
    """
    try:
        return file_service.get_file_info(db, file_path, current_user)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting file info: {str(e)}",
        )


@router.get("/download/{file_path:path}")
def download_resume_file(
    file_path: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session),
):
    """
    Force download resume file (convenience endpoint)

    This is equivalent to calling /files/resume/{file_path}?download=true
    """
    return serve_resume_file(
        file_path=file_path, download=True, current_user=current_user, db=db
    )


@router.get("/view/{file_path:path}")
def view_resume_file(
    file_path: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session),
):
    """
    View resume file inline (convenience endpoint)

    This is equivalent to calling /files/resume/{file_path}?download=false
    Useful for PDFs and images that can be displayed in browser
    """
    return serve_resume_file(
        file_path=file_path, download=False, current_user=current_user, db=db
    )


# Health check endpoint for file service
@router.get("/health")
def file_service_health() -> Dict[str, str]:
    """Health check for file service"""
    try:
        return {
            "status": "healthy",
            "service": "file_service",
            "message": "File serving is operational",
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "file_service",
            "message": f"Error: {str(e)}",
        }


# Simple test endpoint
@router.get("/test")
def test_endpoint() -> Dict[str, str]:
    """Simple test endpoint"""
    return {"status": "working", "message": "Files router test endpoint"}


# Debug endpoint to check file path processing
@router.get("/debug/{file_path:path}")
def debug_resume_file_path(
    file_path: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db_session),
) -> Dict[str, Any]:
    """Debug endpoint to check file path processing"""
    try:
        # Get resume by file path
        resume = file_service._get_resume_by_file_path(db, file_path)

        # Check file existence
        import os
        from pathlib import Path

        # Normalize path for file system check
        normalized_path = file_path
        if normalized_path.startswith("/uploads/"):
            normalized_path = normalized_path[9:]
        elif normalized_path.startswith("uploads/"):
            normalized_path = normalized_path[8:]

        upload_dir = Path(__file__).parent.parent.parent / "uploads"
        full_path = upload_dir / normalized_path
        file_exists = full_path.exists() if not file_path.startswith("http") else False

        return {
            "input_file_path": file_path,
            "normalized_path": normalized_path,
            "full_path": str(full_path)
            if not file_path.startswith("http")
            else "N/A (Google Drive)",
            "file_exists_on_disk": file_exists,
            "resume_found_in_db": resume is not None,
            "resume_id": resume.id if resume else None,
            "resume_db_path": resume.file_path if resume else None,
            "storage_type": "google_drive" if file_path.startswith("http") else "local",
        }

    except Exception as e:
        return {"error": str(e), "input_file_path": file_path}
