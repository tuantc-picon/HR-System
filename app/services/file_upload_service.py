import os
import uuid
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

from fastapi import UploadFile

from config import UPLOAD_CLOUD_TARGET, BASE_DIR

# Optional Google Drive imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    from config import GMAIL_SCOPES
    import io

    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False


class FileUploadService:
    """
    Service for handling file uploads to both local storage and Google Drive
    """

    def __init__(self):
        self.upload_dir = BASE_DIR / "uploads"
        self.upload_dir.mkdir(exist_ok=True)
        self.credentials_file = "credentials.json"
        self.token_file = "token.json"

    def _authenticate_google_drive(self):
        """Authenticate with Google Drive API and return service client"""
        if not GOOGLE_DRIVE_AVAILABLE:
            raise ImportError("Google Drive libraries are not available")

        creds = None
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, GMAIL_SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_file, GMAIL_SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open(self.token_file, "w") as token:
                token.write(creds.to_json())
        return build("drive", "v3", credentials=creds)

    def _generate_unique_filename(self, original_filename: str) -> str:
        """Generate a unique filename to avoid conflicts"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        file_extension = Path(original_filename).suffix
        base_name = Path(original_filename).stem
        return f"{base_name}_{timestamp}_{unique_id}{file_extension}"

    async def upload_file_local(
        self, file: UploadFile, subfolder: str = "resumes"
    ) -> Dict[str, Any]:
        """
        Upload file to local storage

        Args:
            file: The uploaded file
            subfolder: Subfolder within uploads directory

        Returns:
            Dict containing file information
        """
        try:
            # Create subfolder if it doesn't exist
            subfolder_path = self.upload_dir / subfolder
            subfolder_path.mkdir(exist_ok=True)

            # Generate unique filename
            unique_filename = self._generate_unique_filename(file.filename)
            file_path = subfolder_path / unique_filename

            # Save file
            content = await file.read()
            with open(file_path, "wb") as f:
                f.write(content)

            # Return relative path from uploads directory
            relative_path = f"{subfolder}/{unique_filename}"

            return {
                "success": True,
                "file_path": relative_path,
                "full_path": str(file_path),
                "filename": unique_filename,
                "original_filename": file.filename,
                "size": len(content),
                "storage_type": "local",
            }

        except Exception as e:
            return {"success": False, "error": str(e), "storage_type": "local"}

    async def upload_file_google_drive(
        self, file: UploadFile, folder_name: str = "HR_System_Resumes"
    ) -> Dict[str, Any]:
        """
        Upload file to Google Drive

        Args:
            file: The uploaded file
            folder_name: Google Drive folder name

        Returns:
            Dict containing file information
        """
        try:
            if not GOOGLE_DRIVE_AVAILABLE:
                return {
                    "success": False,
                    "error": "Google Drive libraries are not available",
                    "storage_type": "google_drive",
                }

            service = self._authenticate_google_drive()

            # Create or find folder
            folder_id = self._get_or_create_folder(service, folder_name)

            # Generate unique filename
            unique_filename = self._generate_unique_filename(file.filename)

            # Prepare file content
            content = await file.read()
            file_stream = io.BytesIO(content)

            # Upload file
            file_metadata = {"name": unique_filename, "parents": [folder_id]}

            media = MediaIoBaseUpload(
                file_stream,
                mimetype=file.content_type or "application/octet-stream",
                resumable=True,
            )

            uploaded_file = (
                service.files()
                .create(
                    body=file_metadata,
                    media_body=media,
                    fields="id,name,webViewLink,webContentLink",
                )
                .execute()
            )

            return {
                "success": True,
                "file_path": uploaded_file.get("webViewLink"),
                "file_id": uploaded_file.get("id"),
                "download_link": uploaded_file.get("webContentLink"),
                "filename": unique_filename,
                "original_filename": file.filename,
                "size": len(content),
                "storage_type": "google_drive",
                "folder_id": folder_id,
            }

        except Exception as e:
            return {"success": False, "error": str(e), "storage_type": "google_drive"}

    def _get_or_create_folder(self, service, folder_name: str) -> str:
        """Get existing folder or create new one in Google Drive"""
        if not GOOGLE_DRIVE_AVAILABLE:
            raise ImportError("Google Drive libraries are not available")

        # Search for existing folder
        results = (
            service.files()
            .list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                fields="files(id, name)",
            )
            .execute()
        )

        folders = results.get("files", [])

        if folders:
            return folders[0]["id"]

        # Create new folder
        folder_metadata = {
            "name": folder_name,
            "mimeType": "application/vnd.google-apps.folder",
        }

        folder = service.files().create(body=folder_metadata, fields="id").execute()
        return folder.get("id")

    async def upload_file(
        self, file: UploadFile, subfolder: str = "resumes"
    ) -> Dict[str, Any]:
        """
        Upload file based on UPLOAD_CLOUD_TARGET configuration

        Args:
            file: The uploaded file
            subfolder: Subfolder for local storage or folder name for Google Drive

        Returns:
            Dict containing file information
        """
        if UPLOAD_CLOUD_TARGET:
            return await self.upload_file_google_drive(file, subfolder)
        else:
            return await self.upload_file_local(file, subfolder)


# Create singleton instance
file_upload_service = FileUploadService()
