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

- **composite**: Aggregates MCP servers from this repo. Default enabled: data-analysis, pptx, frontend-design, nano-banana, o3, preview. Edit `src/composite/composite-config.yaml` to enable additional servers (xlsx, pdf, docx, vectorstore, browser, dify).

### External MCP Servers

- **filesystem**: File read/write operations ([docs](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem))
- **github**: GitHub API integration ([docs](https://github.com/modelcontextprotocol/servers/tree/main/src/github))
- **memory**: Persistent memory/knowledge graph ([docs](https://github.com/modelcontextprotocol/servers/tree/main/src/memory))
- **fetch**: Web fetching capabilities ([docs](https://github.com/modelcontextprotocol/servers/tree/main/src/fetch))

## Security

- Never commit config files with real tokens to version control
- Add `claude_desktop_config.json` to `.gitignore` if tracking config files
- Consider using environment variables for sensitive values
