# Slack MCP Server

A wrapper around [@ubie-oss/slack-mcp-server](https://github.com/ubie-oss/slack-mcp-server) that integrates with this monorepo's composite server architecture.

## Features

- List channels and users
- Post messages and reply to threads
- Add reactions to messages
- Get channel history and thread replies
- Search messages (requires user token)

## Requirements

- Node.js (for npx to run the npm package)
- Slack Bot Token (`SLACK_BOT_TOKEN`)
- Slack User Token (`SLACK_USER_TOKEN`) - optional, for search

## Setup

1. Create a Slack App at https://api.slack.com/apps
2. Add Bot Token Scopes:
   - `channels:read` - List channels
   - `channels:history` - Read channel messages
   - `chat:write` - Post messages
   - `reactions:write` - Add reactions
   - `users:read` - List users
3. Add User Token Scopes (optional, for search):
   - `search:read` - Search messages
4. Install the app to your workspace
5. Copy tokens to `.env`:

```bash
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_USER_TOKEN=xoxp-your-user-token  # optional
SLACK_SAFE_SEARCH=true  # optional, excludes private channels from search
```

## Tools

| Tool | Description |
|------|-------------|
| `get_workspace_path` | Get workspace directory for Slack files |
| `slack_list_channels` | List public channels with pagination |
| `slack_post_message` | Post a message to a channel |
| `slack_reply_to_thread` | Reply to a message thread |
| `slack_add_reaction` | Add emoji reaction to a message |
| `slack_get_channel_history` | Get recent messages from a channel |
| `slack_get_thread_replies` | Get all replies in a thread |
| `slack_get_users` | List workspace users |
| `slack_get_user_profiles` | Get user profile information |
| `slack_search_messages` | Search messages (requires user token) |

## Testing

```bash
cd src/slack
uv run pytest -v
```

## Usage

Standalone:
```bash
cd src/slack
uv run python -m slack
```

With composite server, add to `composite-config.yaml`:
```yaml
slack:
  enabled: true
  prefix: slack
  module: slack
  description: Slack workspace integration
```

## Security Notes

- **Never commit tokens to git** - Use `.env` files (already in `.gitignore`)
- **Docker deployments**: Environment variables in docker-compose are visible via `docker inspect`. In production, use Docker secrets or external secret management
- **Token rotation**: Rotate tokens regularly, especially user tokens which have broader access
- **Scope minimization**: Only request the OAuth scopes you actually need

## Performance Notes

Each tool call spawns a new `npx` process, which has ~1-2 second overhead due to Node.js startup. For high-frequency operations, consider running the npm server as a persistent service and connecting via HTTP transport.

## Troubleshooting

- **"npx not found"**: Install Node.js 20.x from https://nodejs.org/
- **"No response from Slack API"**: Verify `SLACK_BOT_TOKEN` is set and valid
- **Search not working**: Search requires `SLACK_USER_TOKEN` with `search:read` scope
- **Permission errors**: Ensure your Slack app has been installed to the workspace and has the required scopes
