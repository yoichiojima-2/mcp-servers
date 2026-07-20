# Claude Desktop Configuration Example

Example configuration for using MCP servers with Claude Desktop.

## Setup

1. Copy `claude_desktop_config.json` to the Claude Desktop config directory:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. Update paths (use absolute paths):
   - Replace `/path/to/mcp-servers` with your actual repo path
   - Replace `/Users/username/.mcp-servers` with the directory you want the filesystem server to access

3. Restart Claude Desktop

## Included Servers

### From this repository

- **composite**: Aggregates MCP servers from this repo. Edit `src/composite/composite-config.yaml` to choose which servers are enabled.
- **shell**: Standalone shell server with an explicit command allowlist (`ALLOWED_COMMANDS`).

### External MCP Servers

- **filesystem**: File read/write operations ([docs](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem))
- **memory**: Persistent memory/knowledge graph ([docs](https://github.com/modelcontextprotocol/servers/tree/main/src/memory))

## Security

- Never commit a config containing real tokens or keys to version control
- Keep your personal `claude_desktop_config.json` only in Claude's config directory
- Consider using environment variables for sensitive values
