from __future__ import print_function
import os
import base64
import time
import psycopg2
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import GMAIL_SCOPES


class MyGmail:
    async def gmail_authenticate(self):
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", GMAIL_SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "credentials.json", GMAIL_SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return build("gmail", "v1", credentials=creds)

    async def process_emails(service, user_id="me", max_results=5):
        results = (
            service.users()
            .messages()
            .list(userId=user_id, maxResults=max_results)
            .execute()
        )
        messages = results.get("messages", [])

        if not messages:
            print("📭 No new emails.")
            return

        for msg in messages:
            msg_id = msg["id"]
            message = (
                service.users().messages().get(userId=user_id, id=msg_id).execute()
            )

            if not is_cv_email(message):
                continue

            email_from = ""
            headers = message["payload"].get("headers", [])
            for h in headers:
                if h["name"].lower() == "from":
                    email_from = h["value"]

            parts = message["payload"].get("parts", [])
            for part in parts:
                if part.get("filename"):
                    att_id = part["body"]["attachmentId"]
                    att = (
                        service.users()
                        .messages()
                        .attachments()
                        .get(userId=user_id, messageId=msg_id, id=att_id)
                        .execute()
                    )
                    data = att["data"]
                    file_data = base64.urlsafe_b64decode(data.encode("UTF-8"))

                    save_candidate_and_resume(email_from, part["filename"], file_data)
