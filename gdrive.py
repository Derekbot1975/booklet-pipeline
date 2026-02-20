"""
Google Drive upload integration.

Uploads generated .docx booklets to the correct subject/topic folder
in Google Drive, matching the folder structure from the production guide.

Uses OAuth 2.0 for user authentication (not service account) so you
can upload to your own Drive.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

TOKEN_FILE = Path(__file__).parent / "gdrive_token.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]


def _get_credentials():
    """Get or refresh Google OAuth credentials."""
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request

    creds = None

    # Load existing token
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_secrets = os.getenv("GOOGLE_CLIENT_SECRETS_FILE", "client_secret.json")
            client_secrets_path = Path(__file__).parent / client_secrets
            if not client_secrets_path.exists():
                raise RuntimeError(
                    f"Google client secrets file not found at {client_secrets_path}. "
                    "Download it from console.cloud.google.com > APIs & Services > "
                    "Credentials > OAuth 2.0 Client IDs > Download JSON. "
                    "Save it as client_secret.json in the booklet-pipeline folder."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(client_secrets_path), SCOPES
            )
            creds = flow.run_local_server(port=8090)

        # Save token for next time
        TOKEN_FILE.write_text(creds.to_json())

    return creds


def _get_service():
    """Build Google Drive API service."""
    from googleapiclient.discovery import build
    creds = _get_credentials()
    return build("drive", "v3", credentials=creds)


def _find_or_create_folder(service, name, parent_id=None):
    """Find an existing folder or create a new one."""
    # Search for existing folder
    query = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"

    results = service.files().list(
        q=query, spaces="drive", fields="files(id, name)"
    ).execute()

    files = results.get("files", [])
    if files:
        return files[0]["id"]

    # Create new folder
    metadata = {
        "name": name,
        "mimeType": "application/vnd.google-apps.folder",
    }
    if parent_id:
        metadata["parents"] = [parent_id]

    folder = service.files().create(body=metadata, fields="id").execute()
    return folder["id"]


def _ensure_folder_path(service, path_parts, root_id):
    """
    Ensure a nested folder path exists, creating folders as needed.

    Args:
        service: Drive API service
        path_parts: list of folder names, e.g. ["Biology", "B1 - Cell Biology"]
        root_id: ID of the root folder

    Returns:
        ID of the deepest folder
    """
    current_id = root_id
    for part in path_parts:
        current_id = _find_or_create_folder(service, part, current_id)
    return current_id


def upload_booklet(docx_path, lesson, root_folder_id=None):
    """
    Upload a .docx booklet to the correct Google Drive folder.

    Args:
        docx_path: path to the .docx file
        lesson: lesson dict from parser (used for folder routing)
        root_folder_id: Google Drive folder ID for the root. If None, reads from env.

    Returns:
        dict with file ID and web view link
    """
    from googleapiclient.http import MediaFileUpload

    root_folder_id = root_folder_id or os.getenv("GDRIVE_ROOT_FOLDER_ID")
    if not root_folder_id:
        raise RuntimeError(
            "GDRIVE_ROOT_FOLDER_ID not set. Add it to .env file. "
            "This is the ID of your 'GCSE Combined Science — Self-Study Booklets' "
            "folder in Google Drive."
        )

    docx_path = Path(docx_path)
    service = _get_service()

    # Build folder path from lesson data
    # e.g. output_folder = "Biology/B1 - Cell Biology/"
    output_folder = lesson.get("output_folder", "").strip("/")
    if output_folder:
        path_parts = output_folder.split("/")
    else:
        path_parts = [lesson.get("subject", "Unknown")]

    # Ensure folder path exists
    target_folder_id = _ensure_folder_path(service, path_parts, root_folder_id)

    # Check if file already exists (by name) and update if so
    filename = lesson.get("filename") or docx_path.name
    query = (
        f"name='{filename}' and '{target_folder_id}' in parents and trashed=false"
    )
    existing = service.files().list(
        q=query, spaces="drive", fields="files(id)"
    ).execute().get("files", [])

    media = MediaFileUpload(
        str(docx_path),
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    if existing:
        # Update existing file
        file_id = existing[0]["id"]
        result = service.files().update(
            fileId=file_id, media_body=media, fields="id, webViewLink"
        ).execute()
    else:
        # Create new file
        metadata = {
            "name": filename,
            "parents": [target_folder_id],
        }
        result = service.files().create(
            body=metadata, media_body=media, fields="id, webViewLink"
        ).execute()

    return {
        "file_id": result["id"],
        "web_link": result.get("webViewLink", ""),
        "folder_path": "/".join(path_parts),
        "filename": filename,
    }


def check_connection():
    """Test Google Drive connection and return account info."""
    try:
        service = _get_service()
        about = service.about().get(fields="user").execute()
        user = about.get("user", {})
        return {
            "connected": True,
            "email": user.get("emailAddress", "unknown"),
            "name": user.get("displayName", "unknown"),
        }
    except Exception as e:
        return {
            "connected": False,
            "error": str(e),
        }
