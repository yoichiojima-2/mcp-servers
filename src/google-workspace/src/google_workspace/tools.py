"""Google Workspace MCP tools for Gmail, Drive, Sheets, Docs, Slides, and Calendar."""

import base64
import re
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any

from fastmcp.exceptions import ToolError
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from . import mcp
from .auth import clear_credentials, get_credentials, is_authenticated

# Simple email validation pattern
EMAIL_PATTERN = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")

# Maximum allowed results to prevent API quota exhaustion
MAX_RESULTS_LIMIT = 100


def _sanitize_email_field(value: str) -> str:
    """Remove newlines and control characters to prevent email header injection.

    Args:
        value: The field value to sanitize

    Returns:
        Sanitized string with newlines and carriage returns replaced by spaces
    """
    return value.replace("\n", " ").replace("\r", " ")


def _validate_max_results(max_results: int, field_name: str = "max_results") -> None:
    """Validate max_results is within acceptable bounds.

    Args:
        max_results: The value to validate
        field_name: Name of the field for error messages

    Raises:
        ToolError: If max_results is out of bounds
    """
    if max_results < 1 or max_results > MAX_RESULTS_LIMIT:
        raise ToolError(f"{field_name} must be between 1 and {MAX_RESULTS_LIMIT}")


def _parse_iso_datetime(time_str: str) -> datetime:
    """Parse ISO 8601 datetime string.

    Args:
        time_str: ISO 8601 datetime string

    Returns:
        Parsed datetime object

    Raises:
        ToolError: If the time format is invalid
    """
    try:
        # Handle 'Z' suffix for UTC
        return datetime.fromisoformat(time_str.replace("Z", "+00:00"))
    except ValueError as e:
        raise ToolError(
            f"Invalid time format: {time_str}. Use ISO 8601 format (e.g., 2024-01-15T09:00:00-05:00)"
        ) from e


def _validate_event_times(start_time: str, end_time: str) -> None:
    """Validate that start_time is before end_time.

    Args:
        start_time: Start time in ISO 8601 format
        end_time: End time in ISO 8601 format

    Raises:
        ToolError: If times are invalid or start >= end
    """
    start = _parse_iso_datetime(start_time)
    end = _parse_iso_datetime(end_time)
    if start >= end:
        raise ToolError("start_time must be before end_time")


def _get_service(api: str, version: str) -> Any:
    """Get an authenticated Google API service.

    Args:
        api: The API name (gmail, drive, sheets, docs, slides, calendar)
        version: The API version (v1, v3, v4, etc.)

    Returns:
        The authenticated service object.

    Raises:
        ToolError: If authentication is not configured or fails.
    """
    creds = get_credentials()
    if not creds:
        raise ToolError(
            "Google authentication not configured. "
            "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables, "
            "or place client_secret.json in ~/.mcp-servers/google-workspace/"
        )
    return build(api, version, credentials=creds)


# =============================================================================
# Authentication Tools
# =============================================================================


@mcp.tool()
def google_auth_status() -> dict[str, Any]:
    """Check Google authentication status.

    Returns authentication status and instructions for setting up credentials
    if not authenticated.
    """
    authenticated = is_authenticated()
    return {
        "authenticated": authenticated,
        "message": "Authenticated with Google" if authenticated else "Not authenticated",
        "setup_instructions": None
        if authenticated
        else (
            "To authenticate with Google Workspace:\n"
            "1. Create OAuth credentials in Google Cloud Console\n"
            "2. Set environment variables:\n"
            "   - GOOGLE_CLIENT_ID=your_client_id\n"
            "   - GOOGLE_CLIENT_SECRET=your_client_secret\n"
            "3. Or place client_secret.json in ~/.mcp-servers/google-workspace/\n"
            "4. Call any Google Workspace tool to trigger the OAuth flow"
        ),
    }


@mcp.tool()
def google_auth_logout() -> dict[str, str]:
    """Clear stored Google credentials (logout).

    This removes the stored OAuth tokens, requiring re-authentication
    on the next API call.
    """
    cleared = clear_credentials()
    return {
        "status": "success" if cleared else "no_credentials",
        "message": "Credentials cleared" if cleared else "No credentials to clear",
    }


# =============================================================================
# Gmail Tools
# =============================================================================


@mcp.tool()
def gmail_search(
    query: str,
    max_results: int = 10,
) -> list[dict[str, Any]]:
    """Search Gmail messages.

    Args:
        query: Gmail search query (same syntax as Gmail search box)
               Examples: "from:user@example.com", "subject:meeting", "is:unread"
        max_results: Maximum number of messages to return (default: 10, max: 100)

    Returns:
        List of message summaries with id, threadId, snippet, and headers.
    """
    _validate_max_results(max_results)
    service = _get_service("gmail", "v1")

    try:
        results = service.users().messages().list(userId="me", q=query, maxResults=max_results).execute()

        messages = results.get("messages", [])
        if not messages:
            return []

        # Fetch details for each message
        detailed_messages = []
        for msg in messages:
            msg_data = service.users().messages().get(userId="me", id=msg["id"], format="metadata").execute()

            headers = {h["name"]: h["value"] for h in msg_data.get("payload", {}).get("headers", [])}

            detailed_messages.append(
                {
                    "id": msg_data["id"],
                    "threadId": msg_data["threadId"],
                    "snippet": msg_data.get("snippet", ""),
                    "subject": headers.get("Subject", ""),
                    "from": headers.get("From", ""),
                    "to": headers.get("To", ""),
                    "date": headers.get("Date", ""),
                }
            )

        return detailed_messages
    except HttpError as e:
        raise ToolError(f"Gmail API error: {e}") from e


@mcp.tool()
def gmail_read(
    message_id: str,
) -> dict[str, Any]:
    """Read a Gmail message by ID.

    Args:
        message_id: The message ID (from gmail_search results)

    Returns:
        Full message content including body, headers, and attachments info.
    """
    service = _get_service("gmail", "v1")

    try:
        msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()

        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}

        # Extract body
        body = ""
        payload = msg.get("payload", {})

        def decode_body_data(data: str) -> str:
            """Decode base64 body data with error handling."""
            try:
                return base64.urlsafe_b64decode(data).decode("utf-8")
            except UnicodeDecodeError:
                # Try latin-1 as fallback for non-UTF-8 content
                try:
                    return base64.urlsafe_b64decode(data).decode("latin-1")
                except (UnicodeDecodeError, ValueError):
                    return "[Unable to decode message body]"
            except (ValueError, base64.binascii.Error):
                # Handle invalid base64 data
                return "[Unable to decode message body]"

        def extract_body(part: dict[str, Any], depth: int = 0) -> str:
            """Recursively extract body from message parts."""
            if depth > 10:  # Prevent excessive recursion
                return ""
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    return decode_body_data(data)
            elif part.get("mimeType") == "text/html":
                data = part.get("body", {}).get("data", "")
                if data:
                    return decode_body_data(data)
            elif "parts" in part:
                for subpart in part["parts"]:
                    result = extract_body(subpart, depth + 1)
                    if result:
                        return result
            return ""

        body = extract_body(payload)

        # Extract attachment info recursively
        attachments: list[dict[str, Any]] = []

        def extract_attachments(part: dict[str, Any], depth: int = 0) -> None:
            """Recursively extract attachments from message parts."""
            if depth > 10:  # Prevent excessive recursion
                return
            if part.get("filename"):
                attachments.append(
                    {
                        "filename": part["filename"],
                        "mimeType": part.get("mimeType", ""),
                        "size": part.get("body", {}).get("size", 0),
                    }
                )
            if "parts" in part:
                for subpart in part["parts"]:
                    extract_attachments(subpart, depth + 1)

        extract_attachments(payload)

        return {
            "id": msg["id"],
            "threadId": msg["threadId"],
            "subject": headers.get("Subject", ""),
            "from": headers.get("From", ""),
            "to": headers.get("To", ""),
            "cc": headers.get("Cc", ""),
            "date": headers.get("Date", ""),
            "body": body,
            "attachments": attachments,
            "labelIds": msg.get("labelIds", []),
        }
    except HttpError as e:
        raise ToolError(f"Gmail API error: {e}") from e


def _validate_email_addresses(emails: str, field_name: str) -> None:
    """Validate comma-separated email addresses.

    Args:
        emails: Comma-separated email addresses
        field_name: Name of the field for error message

    Raises:
        ToolError: If any email address is invalid
    """
    for email in emails.split(","):
        email = email.strip()
        if email and not EMAIL_PATTERN.match(email):
            raise ToolError(f"Invalid email address in {field_name}: {email}")


@mcp.tool()
def gmail_send(
    to: str,
    subject: str,
    body: str,
    cc: str | None = None,
    bcc: str | None = None,
    html: bool = False,
) -> dict[str, str]:
    """Send an email via Gmail.

    Args:
        to: Recipient email address(es), comma-separated for multiple
        subject: Email subject
        body: Email body content
        cc: CC recipients (optional)
        bcc: BCC recipients (optional)
        html: If True, treat body as HTML content

    Returns:
        Message ID and thread ID of the sent email.
    """
    # Validate email addresses
    _validate_email_addresses(to, "to")
    if cc:
        _validate_email_addresses(cc, "cc")
    if bcc:
        _validate_email_addresses(bcc, "bcc")

    # Sanitize subject to prevent header injection
    safe_subject = _sanitize_email_field(subject)

    service = _get_service("gmail", "v1")

    try:
        message = MIMEMultipart()
        message["to"] = _sanitize_email_field(to)
        message["subject"] = safe_subject

        if cc:
            message["cc"] = _sanitize_email_field(cc)
        if bcc:
            message["bcc"] = _sanitize_email_field(bcc)

        content_type = "html" if html else "plain"
        message.attach(MIMEText(body, content_type))

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
        result = service.users().messages().send(userId="me", body={"raw": raw}).execute()

        return {
            "status": "sent",
            "id": result["id"],
            "threadId": result["threadId"],
        }
    except HttpError as e:
        raise ToolError(f"Gmail API error: {e}") from e


# =============================================================================
# Google Drive Tools
# =============================================================================


@mcp.tool()
def drive_search(
    query: str | None = None,
    mime_type: str | None = None,
    max_results: int = 10,
) -> list[dict[str, Any]]:
    """Search Google Drive files.

    Args:
        query: Drive search query (optional). Examples:
               - "name contains 'report'"
               - "modifiedTime > '2024-01-01'"
               - "'folder_id' in parents"
        mime_type: Filter by MIME type (optional). Common types:
               - "application/vnd.google-apps.document" (Google Docs)
               - "application/vnd.google-apps.spreadsheet" (Google Sheets)
               - "application/vnd.google-apps.presentation" (Google Slides)
               - "application/pdf"
        max_results: Maximum number of files to return (default: 10, max: 100)

    Returns:
        List of files with id, name, mimeType, and metadata.
    """
    _validate_max_results(max_results)
    service = _get_service("drive", "v3")

    try:
        # Build query
        q_parts = []
        if query:
            q_parts.append(query)
        if mime_type:
            # Escape single quotes to prevent query injection
            safe_mime_type = mime_type.replace("'", "\\'")
            q_parts.append(f"mimeType='{safe_mime_type}'")

        q = " and ".join(q_parts) if q_parts else None

        results = (
            service.files()
            .list(
                q=q,
                pageSize=max_results,
                fields="files(id, name, mimeType, createdTime, modifiedTime, size, webViewLink, parents)",
            )
            .execute()
        )

        return results.get("files", [])
    except HttpError as e:
        raise ToolError(f"Drive API error: {e}") from e


@mcp.tool()
def drive_read(
    file_id: str,
) -> dict[str, Any]:
    """Read a file's content from Google Drive.

    For Google Docs/Sheets/Slides, exports as plain text or appropriate format.
    For other files, returns metadata and download link.

    Args:
        file_id: The file ID from drive_search results

    Returns:
        File metadata and content (for Google Workspace files) or download info.
    """
    service = _get_service("drive", "v3")

    try:
        # Get file metadata
        file_meta = service.files().get(fileId=file_id, fields="id, name, mimeType, webViewLink").execute()

        mime_type = file_meta.get("mimeType", "")
        result = {
            "id": file_meta["id"],
            "name": file_meta["name"],
            "mimeType": mime_type,
            "webViewLink": file_meta.get("webViewLink", ""),
        }

        # Export Google Workspace files as text
        export_mime_map = {
            "application/vnd.google-apps.document": "text/plain",
            "application/vnd.google-apps.spreadsheet": "text/csv",
            "application/vnd.google-apps.presentation": "text/plain",
        }

        if mime_type in export_mime_map:
            content = service.files().export(fileId=file_id, mimeType=export_mime_map[mime_type]).execute()
            result["content"] = content.decode("utf-8") if isinstance(content, bytes) else content
        else:
            result["content"] = None
            result["note"] = "Binary file - use webViewLink to access"

        return result
    except HttpError as e:
        raise ToolError(f"Drive API error: {e}") from e


@mcp.tool()
def drive_create_file(
    name: str,
    content: str,
    mime_type: str = "text/plain",
    parent_folder_id: str | None = None,
) -> dict[str, str]:
    """Create a new file in Google Drive.

    Args:
        name: File name
        content: File content (text)
        mime_type: MIME type of the content (default: text/plain)
        parent_folder_id: Parent folder ID (optional)

    Returns:
        Created file's ID and web link.
    """
    service = _get_service("drive", "v3")

    try:
        from io import BytesIO

        from googleapiclient.http import MediaIoBaseUpload

        file_metadata: dict[str, Any] = {"name": name}
        if parent_folder_id:
            file_metadata["parents"] = [parent_folder_id]

        media = MediaIoBaseUpload(BytesIO(content.encode("utf-8")), mimetype=mime_type, resumable=True)

        file = service.files().create(body=file_metadata, media_body=media, fields="id, webViewLink").execute()

        return {
            "status": "created",
            "id": file["id"],
            "webViewLink": file.get("webViewLink", ""),
        }
    except HttpError as e:
        raise ToolError(f"Drive API error: {e}") from e


# =============================================================================
# Google Sheets Tools
# =============================================================================


@mcp.tool()
def sheets_read(
    spreadsheet_id: str,
    range: str = "Sheet1",
) -> dict[str, Any]:
    """Read data from a Google Sheets spreadsheet.

    Args:
        spreadsheet_id: The spreadsheet ID (from URL or drive_search)
        range: A1 notation range (default: "Sheet1" for entire first sheet)
               Examples: "Sheet1!A1:D10", "Data!A:C"

    Returns:
        Spreadsheet data with values, metadata, and formatting info.
    """
    service = _get_service("sheets", "v4")

    try:
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range).execute()

        # Get spreadsheet metadata
        metadata = service.spreadsheets().get(spreadsheetId=spreadsheet_id, fields="properties.title").execute()

        return {
            "spreadsheetId": spreadsheet_id,
            "title": metadata.get("properties", {}).get("title", ""),
            "range": result.get("range", ""),
            "values": result.get("values", []),
            "rowCount": len(result.get("values", [])),
        }
    except HttpError as e:
        raise ToolError(f"Sheets API error: {e}") from e


@mcp.tool()
def sheets_write(
    spreadsheet_id: str,
    range: str,
    values: list[list[Any]],
) -> dict[str, Any]:
    """Write data to a Google Sheets spreadsheet.

    Args:
        spreadsheet_id: The spreadsheet ID
        range: A1 notation range to write to (e.g., "Sheet1!A1:D10")
        values: 2D array of values to write

    Returns:
        Update result with number of cells updated.
    """
    service = _get_service("sheets", "v4")

    try:
        result = (
            service.spreadsheets()
            .values()
            .update(
                spreadsheetId=spreadsheet_id,
                range=range,
                valueInputOption="USER_ENTERED",
                body={"values": values},
            )
            .execute()
        )

        return {
            "status": "updated",
            "spreadsheetId": result.get("spreadsheetId", ""),
            "updatedRange": result.get("updatedRange", ""),
            "updatedRows": result.get("updatedRows", 0),
            "updatedColumns": result.get("updatedColumns", 0),
            "updatedCells": result.get("updatedCells", 0),
        }
    except HttpError as e:
        raise ToolError(f"Sheets API error: {e}") from e


@mcp.tool()
def sheets_create(
    title: str,
    sheet_names: list[str] | None = None,
) -> dict[str, str]:
    """Create a new Google Sheets spreadsheet.

    Args:
        title: Spreadsheet title
        sheet_names: Optional list of sheet names to create

    Returns:
        Created spreadsheet's ID and URL.
    """
    service = _get_service("sheets", "v4")

    try:
        body: dict[str, Any] = {"properties": {"title": title}}

        if sheet_names:
            body["sheets"] = [{"properties": {"title": name}} for name in sheet_names]

        spreadsheet = service.spreadsheets().create(body=body).execute()

        return {
            "status": "created",
            "spreadsheetId": spreadsheet["spreadsheetId"],
            "spreadsheetUrl": spreadsheet.get("spreadsheetUrl", ""),
        }
    except HttpError as e:
        raise ToolError(f"Sheets API error: {e}") from e


# =============================================================================
# Google Docs Tools
# =============================================================================


@mcp.tool()
def docs_read(
    document_id: str,
) -> dict[str, Any]:
    """Read content from a Google Doc.

    Args:
        document_id: The document ID (from URL or drive_search)

    Returns:
        Document content as plain text with metadata.
    """
    service = _get_service("docs", "v1")

    try:
        doc = service.documents().get(documentId=document_id).execute()

        # Extract text content
        content = []
        for element in doc.get("body", {}).get("content", []):
            if "paragraph" in element:
                for elem in element["paragraph"].get("elements", []):
                    if "textRun" in elem:
                        content.append(elem["textRun"].get("content", ""))

        return {
            "documentId": doc["documentId"],
            "title": doc.get("title", ""),
            "content": "".join(content),
            "revisionId": doc.get("revisionId", ""),
        }
    except HttpError as e:
        raise ToolError(f"Docs API error: {e}") from e


@mcp.tool()
def docs_create(
    title: str,
    content: str | None = None,
) -> dict[str, str]:
    """Create a new Google Doc.

    Args:
        title: Document title
        content: Initial text content (optional)

    Returns:
        Created document's ID and URL.
    """
    service = _get_service("docs", "v1")

    try:
        doc = service.documents().create(body={"title": title}).execute()
        doc_id = doc["documentId"]

        # Add content if provided
        if content:
            requests = [{"insertText": {"location": {"index": 1}, "text": content}}]
            service.documents().batchUpdate(documentId=doc_id, body={"requests": requests}).execute()

        return {
            "status": "created",
            "documentId": doc_id,
            "documentUrl": f"https://docs.google.com/document/d/{doc_id}/edit",
        }
    except HttpError as e:
        raise ToolError(f"Docs API error: {e}") from e


@mcp.tool()
def docs_append(
    document_id: str,
    text: str,
) -> dict[str, str]:
    """Append text to a Google Doc.

    Args:
        document_id: The document ID
        text: Text to append

    Returns:
        Status of the operation.
    """
    service = _get_service("docs", "v1")

    try:
        # Get document to find end index
        doc = service.documents().get(documentId=document_id).execute()
        end_index = doc.get("body", {}).get("content", [{}])[-1].get("endIndex", 1) - 1

        requests = [{"insertText": {"location": {"index": max(1, end_index)}, "text": text}}]

        service.documents().batchUpdate(documentId=document_id, body={"requests": requests}).execute()

        return {
            "status": "appended",
            "documentId": document_id,
        }
    except HttpError as e:
        raise ToolError(f"Docs API error: {e}") from e


# =============================================================================
# Google Slides Tools
# =============================================================================


@mcp.tool()
def slides_read(
    presentation_id: str,
) -> dict[str, Any]:
    """Read content from a Google Slides presentation.

    Args:
        presentation_id: The presentation ID (from URL or drive_search)

    Returns:
        Presentation metadata and slide content summaries.
    """
    service = _get_service("slides", "v1")

    try:
        presentation = service.presentations().get(presentationId=presentation_id).execute()

        slides_info = []
        for i, slide in enumerate(presentation.get("slides", [])):
            slide_content = []
            for element in slide.get("pageElements", []):
                if "shape" in element and "text" in element["shape"]:
                    for text_elem in element["shape"]["text"].get("textElements", []):
                        if "textRun" in text_elem:
                            slide_content.append(text_elem["textRun"].get("content", ""))

            slides_info.append(
                {
                    "slideIndex": i,
                    "slideId": slide.get("objectId", ""),
                    "textContent": "".join(slide_content).strip(),
                }
            )

        return {
            "presentationId": presentation["presentationId"],
            "title": presentation.get("title", ""),
            "slideCount": len(presentation.get("slides", [])),
            "slides": slides_info,
        }
    except HttpError as e:
        raise ToolError(f"Slides API error: {e}") from e


@mcp.tool()
def slides_create(
    title: str,
) -> dict[str, str]:
    """Create a new Google Slides presentation.

    Args:
        title: Presentation title

    Returns:
        Created presentation's ID and URL.
    """
    service = _get_service("slides", "v1")

    try:
        presentation = service.presentations().create(body={"title": title}).execute()

        return {
            "status": "created",
            "presentationId": presentation["presentationId"],
            "presentationUrl": f"https://docs.google.com/presentation/d/{presentation['presentationId']}/edit",
        }
    except HttpError as e:
        raise ToolError(f"Slides API error: {e}") from e


# =============================================================================
# Google Calendar Tools
# =============================================================================


@mcp.tool()
def calendar_list_events(
    calendar_id: str = "primary",
    max_results: int = 10,
    time_min: str | None = None,
    time_max: str | None = None,
) -> list[dict[str, Any]]:
    """List events from a Google Calendar.

    Args:
        calendar_id: Calendar ID (default: "primary" for user's main calendar)
        max_results: Maximum number of events to return (default: 10, max: 100)
        time_min: Filter events starting after this time (ISO 8601 format)
        time_max: Filter events starting before this time (ISO 8601 format)

    Returns:
        List of calendar events with id, summary, start, end, and attendees.
    """
    _validate_max_results(max_results)
    service = _get_service("calendar", "v3")

    try:
        # Default to upcoming events if no time range specified
        if not time_min:
            time_min = datetime.now(timezone.utc).isoformat()

        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = []
        for event in events_result.get("items", []):
            events.append(
                {
                    "id": event["id"],
                    "summary": event.get("summary", "(No title)"),
                    "description": event.get("description", ""),
                    "start": event.get("start", {}).get("dateTime", event.get("start", {}).get("date", "")),
                    "end": event.get("end", {}).get("dateTime", event.get("end", {}).get("date", "")),
                    "location": event.get("location", ""),
                    "attendees": [a.get("email") for a in event.get("attendees", [])],
                    "htmlLink": event.get("htmlLink", ""),
                }
            )

        return events
    except HttpError as e:
        raise ToolError(f"Calendar API error: {e}") from e


@mcp.tool()
def calendar_create_event(
    summary: str,
    start_time: str,
    end_time: str,
    calendar_id: str = "primary",
    description: str | None = None,
    location: str | None = None,
    attendees: list[str] | None = None,
) -> dict[str, str]:
    """Create a new calendar event.

    Args:
        summary: Event title
        start_time: Start time in ISO 8601 format (e.g., "2024-01-15T09:00:00-05:00")
        end_time: End time in ISO 8601 format
        calendar_id: Calendar ID (default: "primary")
        description: Event description (optional)
        location: Event location (optional)
        attendees: List of attendee email addresses (optional)

    Returns:
        Created event's ID and link.
    """
    # Validate event times
    _validate_event_times(start_time, end_time)

    service = _get_service("calendar", "v3")

    try:
        event: dict[str, Any] = {
            "summary": summary,
            "start": {"dateTime": start_time},
            "end": {"dateTime": end_time},
        }

        if description:
            event["description"] = description
        if location:
            event["location"] = location
        if attendees:
            event["attendees"] = [{"email": email} for email in attendees]

        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()

        return {
            "status": "created",
            "eventId": created_event["id"],
            "htmlLink": created_event.get("htmlLink", ""),
        }
    except HttpError as e:
        raise ToolError(f"Calendar API error: {e}") from e


@mcp.tool()
def calendar_update_event(
    event_id: str,
    calendar_id: str = "primary",
    summary: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    description: str | None = None,
    location: str | None = None,
) -> dict[str, str]:
    """Update an existing calendar event.

    Args:
        event_id: Event ID to update
        calendar_id: Calendar ID (default: "primary")
        summary: New event title (optional)
        start_time: New start time in ISO 8601 format (optional)
        end_time: New end time in ISO 8601 format (optional)
        description: New event description (optional)
        location: New event location (optional)

    Returns:
        Updated event's ID and link.
    """
    # Validate time format if provided
    if start_time:
        _parse_iso_datetime(start_time)
    if end_time:
        _parse_iso_datetime(end_time)

    # If both times are provided, validate the range
    if start_time and end_time:
        _validate_event_times(start_time, end_time)

    service = _get_service("calendar", "v3")

    try:
        # Get existing event
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

        # Determine final start and end times for validation
        # Check both dateTime (timed events) and date (all-day events)
        existing_start = event.get("start", {})
        existing_end = event.get("end", {})
        final_start = start_time or existing_start.get("dateTime") or existing_start.get("date")
        final_end = end_time or existing_end.get("dateTime") or existing_end.get("date")

        # Validate the resulting time range when only one time is updated
        # Only validate if both are datetime strings (not date-only strings for all-day events)
        if (start_time or end_time) and final_start and final_end:
            # Skip validation for all-day events (date format: YYYY-MM-DD without time component)
            is_all_day = len(final_start) == 10 or len(final_end) == 10
            if not is_all_day:
                _validate_event_times(final_start, final_end)

        # Update fields
        if summary:
            event["summary"] = summary
        if start_time:
            event["start"] = {"dateTime": start_time}
        if end_time:
            event["end"] = {"dateTime": end_time}
        if description is not None:
            event["description"] = description
        if location is not None:
            event["location"] = location

        updated_event = service.events().update(calendarId=calendar_id, eventId=event_id, body=event).execute()

        return {
            "status": "updated",
            "eventId": updated_event["id"],
            "htmlLink": updated_event.get("htmlLink", ""),
        }
    except HttpError as e:
        raise ToolError(f"Calendar API error: {e}") from e
