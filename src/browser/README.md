# browser

MCP server for browser automation using Playwright with automatic error handling and recovery.

## Features

- **Navigation**: Navigate, go back/forward, reload
- **Content**: Get page content, URL, title
- **Interaction**: Click, fill forms, type text, press keys, hover
- **Screenshots**: Save to file or get as base64
- **JavaScript**: Execute scripts in the browser
- **Wait Functions**: Wait for selectors or navigation
- **Robustness**: Thread-safe operations, automatic error recovery, page health monitoring

## Tools

| Tool | Description |
|------|-------------|
| `navigate` | Navigate to a URL |
| `go_back`, `go_forward`, `reload` | Navigation controls |
| `get_content` | Get text content (handles large pages) |
| `get_url`, `get_title` | Get page info |
| `click`, `fill`, `type_text` | Form interaction |
| `press_key`, `select_option`, `hover` | Input controls |
| `screenshot`, `screenshot_base64` | Capture screenshots |
| `evaluate` | Execute JavaScript |
| `wait_for_selector`, `wait_for_navigation` | Wait functions |
| `close_browser`, `force_reset`, `get_page_status` | Browser management |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `HEADLESS` | `false` | Run browser in headless mode |
| `BROWSER_TIMEOUT` | `30000` | Default timeout for operations (ms) |
| `NAVIGATION_TIMEOUT` | `60000` | Timeout for page navigation (ms) |
| `NO_SANDBOX` | `false` | Disable browser sandbox (use with caution) |

Screenshots are saved to `~/.mcp-servers/workspace/`. Use the `get_workspace_path()` tool to get the path.

### Stability Tuning

| Variable | Default | Description |
|----------|---------|-------------|
| `HEALTH_CHECK_TIMEOUT` | `10.0` | Page health check timeout (seconds) |
| `CONTENT_EVAL_TIMEOUT` | `20.0` | Content evaluation timeout (seconds) |
| `SCRIPT_EVAL_TIMEOUT` | `60.0` | JavaScript execution timeout (seconds) |

If you experience timeouts, increase these values.

## Troubleshooting

### "This isn't working right now" Error

1. **Increase timeouts**: Set `HEALTH_CHECK_TIMEOUT=15.0`, `CONTENT_EVAL_TIMEOUT=30.0`
2. **Check page health**: Use `get_page_status()` tool
3. **Force reset**: Use `force_reset()` or `close_browser()` to recover
4. **Check logs**: `~/Library/Logs/Claude/mcp-server-browser.log`

### Large Pages
Use `get_content(max_length=...)` to control output size, or use `evaluate()` to extract specific data.

## Usage

```bash
uv run python -m browser
```

See [server guide](../../docs/server-guide.md) for common CLI options.
