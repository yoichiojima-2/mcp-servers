"""OAuth2 authentication for Google Workspace APIs."""

import json
import os
from pathlib import Path
from typing import Any

from core import get_workspace
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes for Google Workspace APIs
SCOPES = [
    # Gmail
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    # Drive
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.file",
    # Sheets
    "https://www.googleapis.com/auth/spreadsheets",
    # Docs
    "https://www.googleapis.com/auth/documents",
    # Slides
    "https://www.googleapis.com/auth/presentations",
    # Calendar
    "https://www.googleapis.com/auth/calendar",
]

# Workspace directory for storing credentials
WORKSPACE = get_workspace("google-workspace")
TOKEN_PATH = WORKSPACE / "token.json"


def _get_client_config() -> dict[str, Any] | None:
    """Get OAuth client configuration from environment or file.

    Priority:
    1. Environment variables (GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
    2. GOOGLE_CLIENT_SECRET_PATH environment variable
    3. client_secret.json in workspace directory
    """
    # Try environment variables first
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

    if client_id and client_secret:
        return {
            "installed": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost"],
            }
        }

    # Try client_secret.json path from environment
    secret_path = os.getenv("GOOGLE_CLIENT_SECRET_PATH")
    if secret_path:
        path = Path(secret_path)
        if path.exists():
            try:
                with open(path) as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return None

    # Try workspace directory
    workspace_secret = WORKSPACE / "client_secret.json"
    if workspace_secret.exists():
        try:
            with open(workspace_secret) as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None

    return None


def get_credentials() -> Credentials | None:
    """Get valid Google credentials, refreshing or authenticating as needed.

    Returns:
        Valid credentials or None if authentication is not configured.
    """
    creds = None

    # Load existing token
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    # If no valid credentials, try to refresh or authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            client_config = _get_client_config()
            if not client_config:
                return None

            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for future use with secure permissions
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
        TOKEN_PATH.chmod(0o600)  # Owner read/write only

    return creds


def clear_credentials() -> bool:
    """Clear stored credentials.

    Returns:
        True if credentials were cleared, False if none existed.
    """
    if TOKEN_PATH.exists():
        TOKEN_PATH.unlink()
        return True
    return False


def is_authenticated() -> bool:
    """Check if valid credentials exist.

    Returns:
        True if valid credentials exist, False otherwise.
    """
    if not TOKEN_PATH.exists():
        return False

    try:
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        return creds.valid or (creds.expired and creds.refresh_token is not None)
    except (ValueError, json.JSONDecodeError, KeyError):
        # Handle malformed token files
        return False
