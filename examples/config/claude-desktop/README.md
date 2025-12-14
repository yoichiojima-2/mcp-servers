# Claude Desktop Configuration Example

Example configuration for using MCP servers with Claude Desktop.

## Setup

1. Copy `claude_desktop_config.json` to Claude Desktop config directory:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. Update paths and tokens:
   - Replace `/path/to/mcp-servers` with your actual repo path
   - Replace `/Users/username/...` with your actual paths for filesystem access
   - Replace `<your-github-token>` with your GitHub personal access token

3. Restart Claude Desktop

## Included Servers

### From this repository

- **composite**: Aggregates all MCP servers from this repo (data-analysis, xlsx, pdf, docx, pptx, vectorstore, browser, frontend-design, nano-banana, dify, o3, preview)

### External MCP Servers

- **filesystem**: File read/write operations ([docs](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem))
- **github**: GitHub API integration ([docs](https://github.com/modelcontextprotocol/servers/tree/main/src/github))
- **memory**: Persistent memory/knowledge graph ([docs](https://github.com/modelcontextprotocol/servers/tree/main/src/memory))
- **fetch**: Web fetching capabilities ([docs](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch))
