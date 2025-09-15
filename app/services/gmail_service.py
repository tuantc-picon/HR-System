import os
import base64
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import GMAIL_SCOPES


class GmailService:
    """
    Common Gmail Service class
    - Authenticate with Gmail API
    - Fetch emails
    - Filter CV emails
    - Download attachments
    """

    def __init__(
        self,
        credentials_file: str = "credentials.json",
        token_file: str = "token.json",
        download_dir: str = "downloads"
    ):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        self.service = self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API and return service client"""
        creds = None
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, GMAIL_SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, GMAIL_SCOPES)
                creds = flow.run_local_server(port=0)
            with open(self.token_file, "w") as token:
                token.write(creds.to_json())
        return build("gmail", "v1", credentials=creds)

    # ------------------------------
    # Helpers
    # ------------------------------
    def _extract_header(self, message, name: str) -> Optional[str]:
        headers = message.get("payload", {}).get("headers", [])
        for h in headers:
            if h["name"].lower() == name.lower():
                return h["value"]
        return None

    def _is_cv_email(self, message) -> bool:
        subject = self._extract_header(message, "Subject") or ""
        parts = message.get("payload", {}).get("parts", [])
        has_attachment = any(p.get("filename") for p in parts if p.get("filename"))
        keywords = ["cv", "resume", "ứng tuyển", "apply"]

        if has_attachment and any(kw in subject.lower() for kw in keywords):
            return True
        return False

    def _download_attachments(self, message, msg_id: str) -> List[Dict]:
        attachments = []
        parts = message.get("payload", {}).get("parts", [])
        for part in parts:
            if part.get("filename"):
                att_id = part["body"]["attachmentId"]
                att = self.service.users().messages().attachments().get(
                    userId="me", messageId=msg_id, id=att_id
                ).execute()
                data = att["data"]
                file_data = base64.urlsafe_b64decode(data.encode("UTF-8"))

                filepath = os.path.join(self.download_dir, part["filename"])
                with open(filepath, "wb") as f:
                    f.write(file_data)

                attachments.append({
                    "file_name": part["filename"],
                    "file_path": filepath
                })
        return attachments

    # ------------------------------
    # Public methods
    # ------------------------------
    def fetch_cv_emails(self, max_results: int = 10) -> List[Dict]:
        """
        Fetch CV emails and return metadata:
        [
            {
                "email": "sender@example.com",
                "subject": "Apply for Developer",
                "attachments": [
                    {"file_name": "cv_john.pdf", "file_path": "downloads/cv_john.pdf"}
                ]
            }
        ]
        """
        results = self.service.users().messages().list(
            userId="me",
            maxResults=max_results
        ).execute()

        messages = results.get("messages", [])
        candidates = []

        for msg in messages:
            msg_id = msg["id"]
            message = self.service.users().messages().get(userId="me", id=msg_id).execute()

            if not self._is_cv_email(message):
                continue

            sender = self._extract_header(message, "From")
            subject = self._extract_header(message, "Subject")
            attachments = self._download_attachments(message, msg_id)

            candidates.append({
                "email": sender,
                "subject": subject,
                "attachments": attachments
            })

        return candidates

