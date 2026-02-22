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
SCOPES = ["https://www.googleapis.com/auth/drive"]


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
            creds = flow.run_local_server(port=0)

        # Save token for next time
        TOKEN_FILE.write_text(creds.to_json())

    return creds


def _get_service():
    """Build Google Drive API service."""
    from googleapiclient.discovery import build
    creds = _get_credentials()
    return build("drive", "v3", credentials=creds)


def _escape_query(value):
    """Escape a value for use in a Google Drive API query string."""
    return value.replace("\\", "\\\\").replace("'", "\\'")


def _find_or_create_folder(service, name, parent_id=None):
    """Find an existing folder or create a new one."""
    # Search for existing folder
    safe_name = _escape_query(name)
    query = f"name='{safe_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
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


MIME_TYPES = {
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pdf": "application/pdf",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


def _resolve_folder(service, lesson, root_folder_id):
    """Resolve (and create if needed) the target Drive folder for a lesson.

    The root_folder_id can be overridden per-course. The output_folder on the
    lesson already includes a course_id prefix (e.g. "aqa-combined-science/Biology/B1/")
    which keeps different courses separated in Drive.
    """
    root_folder_id = root_folder_id or os.getenv("GDRIVE_ROOT_FOLDER_ID")
    if not root_folder_id:
        raise RuntimeError(
            "GDRIVE_ROOT_FOLDER_ID not set. Add it to .env file or "
            "set a per-course Google Drive folder ID in the course settings."
        )
    output_folder = lesson.get("output_folder", "").strip("/")
    if output_folder:
        path_parts = output_folder.split("/")
    else:
        path_parts = [lesson.get("subject", "Unknown")]
    folder_id = _ensure_folder_path(service, path_parts, root_folder_id)
    return folder_id, path_parts


def _upload_single_file(service, file_path, folder_id):
    """
    Upload or update a single file in a Drive folder.

    Returns dict with file_id, web_link, and filename.
    """
    from googleapiclient.http import MediaFileUpload

    file_path = Path(file_path)
    filename = file_path.name
    ext = file_path.suffix.lower()
    mimetype = MIME_TYPES.get(ext, "application/octet-stream")

    # Check if file already exists (by name) and update if so
    safe_filename = _escape_query(filename)
    query = (
        f"name='{safe_filename}' and '{folder_id}' in parents and trashed=false"
    )
    existing = service.files().list(
        q=query, spaces="drive", fields="files(id)"
    ).execute().get("files", [])

    media = MediaFileUpload(str(file_path), mimetype=mimetype)

    if existing:
        file_id = existing[0]["id"]
        result = service.files().update(
            fileId=file_id, media_body=media, fields="id, webViewLink"
        ).execute()
    else:
        metadata = {"name": filename, "parents": [folder_id]}
        result = service.files().create(
            body=metadata, media_body=media, fields="id, webViewLink"
        ).execute()

    return {
        "file_id": result["id"],
        "web_link": result.get("webViewLink", ""),
        "filename": filename,
    }


def upload_booklet(docx_path, lesson, root_folder_id=None):
    """
    Upload .docx and .pdf booklet files to the correct Google Drive folder.

    Uploads the .docx first. If a matching .pdf exists alongside it,
    that is uploaded too.

    Args:
        docx_path: path to the .docx file
        lesson: lesson dict from parser (used for folder routing)
        root_folder_id: Google Drive folder ID for the root.

    Returns:
        dict with results for each uploaded file
    """
    docx_path = Path(docx_path)
    service = _get_service()
    folder_id, path_parts = _resolve_folder(service, lesson, root_folder_id)
    folder_path = "/".join(path_parts)

    results = {"folder_path": folder_path, "files": []}

    # Upload .docx
    docx_result = _upload_single_file(service, docx_path, folder_id)
    results["files"].append(docx_result)

    # Upload .pdf if it exists
    pdf_path = docx_path.with_suffix(".pdf")
    if pdf_path.exists():
        pdf_result = _upload_single_file(service, pdf_path, folder_id)
        results["files"].append(pdf_result)

    # Backward-compatible top-level fields (from the docx upload)
    results["file_id"] = docx_result["file_id"]
    results["web_link"] = docx_result["web_link"]
    results["filename"] = docx_result["filename"]

    return results


def delete_lesson_files_from_drive(lesson, root_folder_id=None):
    """Delete booklet files for a lesson from Google Drive.

    Searches for files matching the lesson number prefix in the resolved
    folder path. Returns dict with 'deleted' and 'errors' lists.
    """
    service = _get_service()
    root_folder_id = root_folder_id or os.getenv("GDRIVE_ROOT_FOLDER_ID")
    if not root_folder_id:
        return {"deleted": [], "errors": ["No Drive root folder configured"]}

    result = {"deleted": [], "errors": []}
    search_prefix = f"L{lesson['lesson_number']:03d} - "

    # Try to find the folder; fall back to root if not found
    try:
        folder_id, _ = _resolve_folder(service, lesson, root_folder_id)
    except Exception:
        folder_id = root_folder_id

    safe_prefix = _escape_query(search_prefix)
    query = (
        f"name contains '{safe_prefix}' and "
        f"'{folder_id}' in parents and "
        f"trashed=false"
    )

    try:
        files = service.files().list(
            q=query, spaces="drive", fields="files(id, name)"
        ).execute().get("files", [])

        for f in files:
            try:
                service.files().delete(fileId=f["id"]).execute()
                result["deleted"].append(f["name"])
            except Exception as e:
                result["errors"].append(f"Failed to delete {f['name']}: {e}")
    except Exception as e:
        result["errors"].append(f"Search failed: {e}")

    return result


def upload_as_google_native(local_path, name, target_mime, folder_id=None):
    """
    Upload a local file to Google Drive, converting to a Google-native format.

    Setting the target mimeType in metadata triggers automatic conversion
    (e.g. .xlsx → Google Sheets, .docx → Google Docs).

    Args:
        local_path: path to the local file (.xlsx or .docx)
        name: desired name in Google Drive
        target_mime: Google MIME type, e.g.:
            "application/vnd.google-apps.spreadsheet" (Google Sheets)
            "application/vnd.google-apps.document" (Google Docs)
        folder_id: optional Drive folder ID (defaults to GDRIVE_ROOT_FOLDER_ID)

    Returns:
        dict with file_id and web_link
    """
    from googleapiclient.http import MediaFileUpload

    service = _get_service()
    local_path = Path(local_path)

    ext = local_path.suffix.lower()
    source_mime = MIME_TYPES.get(ext, "application/octet-stream")

    folder_id = folder_id or os.getenv("GDRIVE_ROOT_FOLDER_ID")

    metadata = {
        "name": name,
        "mimeType": target_mime,
    }
    if folder_id:
        metadata["parents"] = [folder_id]

    media = MediaFileUpload(str(local_path), mimetype=source_mime)

    result = service.files().create(
        body=metadata,
        media_body=media,
        fields="id, webViewLink",
    ).execute()

    return {
        "file_id": result["id"],
        "web_link": result.get("webViewLink", ""),
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
