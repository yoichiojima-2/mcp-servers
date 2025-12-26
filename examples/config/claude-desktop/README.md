# Claude Desktop Configuration Example

Example configuration for using MCP servers with Claude Desktop.

## Setup

1. Copy `claude_desktop_config.json` to Claude Desktop config directory:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Update paths and tokens (use absolute paths):
   - Replace `/path/to/mcp-servers` with your actual repo path (e.g., `/Users/yo/Developer/mcp-servers`)
   - Replace `/path/to/documents` and `/path/to/desktop` with directories you want Claude to access
   - Replace `<your-github-token>` with your GitHub personal access token

3. Restart Claude Desktop

## Included Servers

### From this repository

- **composite**: Aggregates MCP servers from this repo. Default enabled: shell, skills. Edit `src/composite/composite-config.yaml` to enable additional servers (data-analysis, xlsx, pdf, docx, pptx, vectorstore, browser, dify, frontend-design, nano-banana, o3, preview, img2pptx).

### External MCP Servers

- **filesystem**: File read/write operations ([docs](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem))
- **github**: GitHub API integration ([docs](https://github.com/modelcontextprotocol/servers/tree/main/src/github))
- **memory**: Persistent memory/knowledge graph ([docs](https://github.com/modelcontextprotocol/servers/tree/main/src/memory))
- **fetch**: Web fetching capabilities ([docs](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch))

## Security

- Never commit your actual config with real tokens to version control
- Keep your personal `claude_desktop_config.json` only in Claude's config directory
- Consider using environment variables for sensitive values
