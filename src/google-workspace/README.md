# Google Workspace MCP Server

MCP server for Google Workspace integration (Gmail, Drive, Sheets, Docs, Slides, Calendar).

## Features

- **Gmail**: Search, read, and send emails
- **Google Drive**: Search files, read content, create files
- **Google Sheets**: Read, write, and create spreadsheets
- **Google Docs**: Read, create, and append to documents
- **Google Slides**: Read and create presentations
- **Google Calendar**: List, create, and update events

## Requirements

- Python 3.12+
- Google Cloud project with OAuth credentials
- Enabled Google Workspace APIs

## Setup

### 1. Create Google Cloud OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Gmail API
   - Google Drive API
   - Google Sheets API
   - Google Docs API
   - Google Slides API
   - Google Calendar API
4. Go to "APIs & Services" > "Credentials"
5. Click "Create Credentials" > "OAuth client ID"
6. Select "Desktop app" as the application type
7. Download the credentials JSON file

### 2. Configure Credentials

Choose one of these methods:

**Option A: Environment Variables (Recommended)**
```bash
export GOOGLE_CLIENT_ID="your_client_id"
export GOOGLE_CLIENT_SECRET="your_client_secret"
```

**Option B: Client Secret File Path**
```bash
export GOOGLE_CLIENT_SECRET_PATH="/path/to/client_secret.json"
```

**Option C: Default Location**
Place `client_secret.json` in `~/.mcp-servers/google-workspace/`

### 3. First-Time Authentication

On first use, the server will:
1. Open a browser window for Google OAuth consent
2. Request permission for the configured scopes
3. Store the refresh token in `~/.mcp-servers/google-workspace/token.json`

## Tools

### Authentication

| Tool | Description |
|------|-------------|
| `google_auth_status` | Check authentication status |
| `google_auth_logout` | Clear stored credentials |

### Gmail

| Tool | Description |
|------|-------------|
| `gmail_search` | Search emails using Gmail query syntax |
| `gmail_read` | Read a specific email by ID |
| `gmail_send` | Send an email |

### Google Drive

| Tool | Description |
|------|-------------|
| `drive_search` | Search files in Drive |
| `drive_read` | Read file content or metadata |
| `drive_create_file` | Create a new file |

### Google Sheets

| Tool | Description |
|------|-------------|
| `sheets_read` | Read data from a spreadsheet |
| `sheets_write` | Write data to a spreadsheet |
| `sheets_create` | Create a new spreadsheet |

### Google Docs

| Tool | Description |
|------|-------------|
| `docs_read` | Read document content |
| `docs_create` | Create a new document |
| `docs_append` | Append text to a document |

### Google Slides

| Tool | Description |
|------|-------------|
| `slides_read` | Read presentation content |
| `slides_create` | Create a new presentation |

### Google Calendar

| Tool | Description |
|------|-------------|
| `calendar_list_events` | List calendar events |
| `calendar_create_event` | Create a new event |
| `calendar_update_event` | Update an existing event |

## Installation

```bash
# From repository root
uv sync --dev

# Run the server
cd src/google-workspace
uv run python -m google_workspace
```

## Testing

```bash
cd src/google-workspace
uv run pytest -v
```

## Docker Usage

The OAuth flow requires a browser for first-time authentication. For Docker deployments:

1. **Authenticate locally first**:
   ```bash
   # Run the server locally to complete OAuth flow
   cd src/google-workspace
   uv run python -m google_workspace
   # A browser will open - complete the Google sign-in
   ```

2. **Mount the token directory in Docker**:
   ```yaml
   # docker-compose.yml
   volumes:
     - ~/.mcp-servers/google-workspace:/root/.mcp-servers/google-workspace
   ```

Alternatively, the token.json file can be copied to the container after local authentication.

## Security Notes

- **Never commit credentials**: Keep `client_secret.json` and `token.json` out of version control
- **Minimal scopes**: The server requests only necessary OAuth scopes
- **Token storage**: Refresh tokens are stored in `~/.mcp-servers/google-workspace/` with owner-only permissions (0600)
- **Logout option**: Use `google_auth_logout` to clear stored credentials

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GOOGLE_CLIENT_ID` | OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | OAuth client secret |
| `GOOGLE_CLIENT_SECRET_PATH` | Path to client_secret.json |
