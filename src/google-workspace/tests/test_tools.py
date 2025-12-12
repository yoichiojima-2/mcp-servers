"""Tests for Google Workspace tools."""

import json
from unittest.mock import MagicMock, patch

import pytest
from fastmcp import Client
from fastmcp.exceptions import ToolError

from google_workspace import mcp


@pytest.fixture
def mock_credentials():
    """Mock Google credentials."""
    with patch("google_workspace.tools.get_credentials") as mock:
        creds = MagicMock()
        creds.valid = True
        mock.return_value = creds
        yield mock


@pytest.fixture
def mock_gmail_service():
    """Mock Gmail service."""
    with patch("google_workspace.tools.build") as mock_build:
        service = MagicMock()
        mock_build.return_value = service
        yield service


@pytest.fixture
def mock_drive_service():
    """Mock Drive service."""
    with patch("google_workspace.tools.build") as mock_build:
        service = MagicMock()
        mock_build.return_value = service
        yield service


@pytest.fixture
def mock_sheets_service():
    """Mock Sheets service."""
    with patch("google_workspace.tools.build") as mock_build:
        service = MagicMock()
        mock_build.return_value = service
        yield service


@pytest.mark.asyncio
async def test_google_auth_status_not_authenticated():
    """Test auth status when not authenticated."""
    with patch("google_workspace.tools.is_authenticated", return_value=False):
        async with Client(mcp) as client:
            result = await client.call_tool("google_auth_status", {})
            assert result.content
            data = json.loads(result.content[0].text)
            assert data["authenticated"] is False
            assert "setup_instructions" in data


@pytest.mark.asyncio
async def test_google_auth_status_authenticated():
    """Test auth status when authenticated."""
    with patch("google_workspace.tools.is_authenticated", return_value=True):
        async with Client(mcp) as client:
            result = await client.call_tool("google_auth_status", {})
            assert result.content
            data = json.loads(result.content[0].text)
            assert data["authenticated"] is True


@pytest.mark.asyncio
async def test_google_auth_logout():
    """Test logout clears credentials."""
    with patch("google_workspace.tools.clear_credentials", return_value=True):
        async with Client(mcp) as client:
            result = await client.call_tool("google_auth_logout", {})
            assert result.content
            data = eval(result.content[0].text)
            assert data["status"] == "success"


@pytest.mark.asyncio
async def test_gmail_search(mock_credentials, mock_gmail_service):
    """Test Gmail search."""
    # Setup mock response
    mock_gmail_service.users().messages().list().execute.return_value = {
        "messages": [{"id": "msg1", "threadId": "thread1"}]
    }
    mock_gmail_service.users().messages().get().execute.return_value = {
        "id": "msg1",
        "threadId": "thread1",
        "snippet": "Test snippet",
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Test Subject"},
                {"name": "From", "value": "test@example.com"},
                {"name": "To", "value": "me@example.com"},
                {"name": "Date", "value": "2024-01-01"},
            ]
        },
    }

    async with Client(mcp) as client:
        result = await client.call_tool("gmail_search", {"query": "test"})
        assert result.content
        data = eval(result.content[0].text)
        assert len(data) == 1
        assert data[0]["id"] == "msg1"
        assert data[0]["subject"] == "Test Subject"


@pytest.mark.asyncio
async def test_gmail_read(mock_credentials, mock_gmail_service):
    """Test Gmail read."""
    import base64

    body_content = base64.urlsafe_b64encode(b"Test email body").decode("utf-8")
    mock_gmail_service.users().messages().get().execute.return_value = {
        "id": "msg1",
        "threadId": "thread1",
        "payload": {
            "mimeType": "text/plain",
            "headers": [
                {"name": "Subject", "value": "Test Subject"},
                {"name": "From", "value": "test@example.com"},
            ],
            "body": {"data": body_content},
        },
        "labelIds": ["INBOX"],
    }

    async with Client(mcp) as client:
        result = await client.call_tool("gmail_read", {"message_id": "msg1"})
        assert result.content
        data = eval(result.content[0].text)
        assert data["id"] == "msg1"
        assert data["subject"] == "Test Subject"
        assert "Test email body" in data["body"]


@pytest.mark.asyncio
async def test_gmail_send(mock_credentials, mock_gmail_service):
    """Test Gmail send."""
    mock_gmail_service.users().messages().send().execute.return_value = {"id": "sent1", "threadId": "thread1"}

    async with Client(mcp) as client:
        result = await client.call_tool(
            "gmail_send",
            {
                "to": "recipient@example.com",
                "subject": "Test Subject",
                "body": "Test body",
            },
        )
        assert result.content
        data = eval(result.content[0].text)
        assert data["status"] == "sent"
        assert data["id"] == "sent1"


@pytest.mark.asyncio
async def test_drive_search(mock_credentials, mock_drive_service):
    """Test Drive search."""
    mock_drive_service.files().list().execute.return_value = {
        "files": [
            {
                "id": "file1",
                "name": "Test Document",
                "mimeType": "application/vnd.google-apps.document",
            }
        ]
    }

    async with Client(mcp) as client:
        result = await client.call_tool("drive_search", {"query": "name contains 'Test'"})
        assert result.content
        data = eval(result.content[0].text)
        assert len(data) == 1
        assert data[0]["name"] == "Test Document"


@pytest.mark.asyncio
async def test_sheets_read(mock_credentials, mock_sheets_service):
    """Test Sheets read."""
    mock_sheets_service.spreadsheets().values().get().execute.return_value = {
        "range": "Sheet1!A1:B2",
        "values": [["Header1", "Header2"], ["Value1", "Value2"]],
    }
    mock_sheets_service.spreadsheets().get().execute.return_value = {"properties": {"title": "Test Sheet"}}

    async with Client(mcp) as client:
        result = await client.call_tool(
            "sheets_read",
            {"spreadsheet_id": "test-id", "range": "Sheet1!A1:B2"},
        )
        assert result.content
        data = eval(result.content[0].text)
        assert data["title"] == "Test Sheet"
        assert data["rowCount"] == 2


@pytest.mark.asyncio
async def test_sheets_create(mock_credentials, mock_sheets_service):
    """Test Sheets create."""
    mock_sheets_service.spreadsheets().create().execute.return_value = {
        "spreadsheetId": "new-sheet-id",
        "spreadsheetUrl": "https://docs.google.com/spreadsheets/d/new-sheet-id",
    }

    async with Client(mcp) as client:
        result = await client.call_tool("sheets_create", {"title": "New Sheet"})
        assert result.content
        data = eval(result.content[0].text)
        assert data["status"] == "created"
        assert data["spreadsheetId"] == "new-sheet-id"


@pytest.mark.asyncio
async def test_calendar_list_events(mock_credentials):
    """Test Calendar list events."""
    with patch("google_workspace.tools.build") as mock_build:
        service = MagicMock()
        mock_build.return_value = service
        service.events().list().execute.return_value = {
            "items": [
                {
                    "id": "event1",
                    "summary": "Test Meeting",
                    "start": {"dateTime": "2024-01-15T09:00:00-05:00"},
                    "end": {"dateTime": "2024-01-15T10:00:00-05:00"},
                    "htmlLink": "https://calendar.google.com/event?eid=event1",
                }
            ]
        }

        async with Client(mcp) as client:
            result = await client.call_tool("calendar_list_events", {"max_results": 10})
            assert result.content
            data = eval(result.content[0].text)
            assert len(data) == 1
            assert data[0]["summary"] == "Test Meeting"


@pytest.mark.asyncio
async def test_docs_read(mock_credentials):
    """Test Docs read."""
    with patch("google_workspace.tools.build") as mock_build:
        service = MagicMock()
        mock_build.return_value = service
        service.documents().get().execute.return_value = {
            "documentId": "doc1",
            "title": "Test Document",
            "revisionId": "rev1",
            "body": {
                "content": [
                    {"paragraph": {"elements": [{"textRun": {"content": "Hello, "}}]}},
                    {"paragraph": {"elements": [{"textRun": {"content": "World!"}}]}},
                ]
            },
        }

        async with Client(mcp) as client:
            result = await client.call_tool("docs_read", {"document_id": "doc1"})
            assert result.content
            data = eval(result.content[0].text)
            assert data["title"] == "Test Document"
            assert "Hello" in data["content"]


@pytest.mark.asyncio
async def test_slides_read(mock_credentials):
    """Test Slides read."""
    with patch("google_workspace.tools.build") as mock_build:
        service = MagicMock()
        mock_build.return_value = service
        service.presentations().get().execute.return_value = {
            "presentationId": "pres1",
            "title": "Test Presentation",
            "slides": [
                {
                    "objectId": "slide1",
                    "pageElements": [
                        {"shape": {"text": {"textElements": [{"textRun": {"content": "Slide 1 Title"}}]}}}
                    ],
                }
            ],
        }

        async with Client(mcp) as client:
            result = await client.call_tool("slides_read", {"presentation_id": "pres1"})
            assert result.content
            data = eval(result.content[0].text)
            assert data["title"] == "Test Presentation"
            assert data["slideCount"] == 1


@pytest.mark.asyncio
async def test_tool_error_without_credentials():
    """Test that tools raise appropriate error without credentials."""
    with patch("google_workspace.tools.get_credentials", return_value=None):
        async with Client(mcp) as client:
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool("gmail_search", {"query": "test"})
            # Should contain error about authentication
            assert "authentication" in str(exc_info.value).lower()
