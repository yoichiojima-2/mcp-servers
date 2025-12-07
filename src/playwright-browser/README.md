# Playwright Browser MCP Server

MCP server for browser automation using the official Microsoft Playwright MCP package.

## Installation

```bash
npm install
npx playwright install chromium
```

## Usage

### Run the MCP server

```bash
# Headless mode (default)
npm start

# Headed mode (visible browser)
npm run start:headed
```

### Configure in Claude Code

```bash
claude mcp add playwright -- npx @playwright/mcp
```

Or add to your MCP settings:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp"]
    }
  }
}
```

## Available Tools

The server provides these browser automation tools:

- `browser_navigate` - Navigate to a URL
- `browser_snapshot` - Capture accessibility snapshot of the page
- `browser_click` - Click an element
- `browser_type` - Type text into an element
- `browser_fill_form` - Fill multiple form fields
- `browser_select_option` - Select dropdown option
- `browser_hover` - Hover over element
- `browser_drag` - Drag and drop
- `browser_press_key` - Press keyboard key
- `browser_take_screenshot` - Take a screenshot
- `browser_evaluate` - Execute JavaScript
- `browser_tabs` - Manage browser tabs
- `browser_wait_for` - Wait for conditions
- `browser_close` - Close the browser

## Options

```bash
npx @playwright/mcp --help
```

Key options:
- `--headed` - Run in headed mode (visible browser)
- `--browser <browser>` - Browser type: chromium, firefox, webkit
- `--viewport-size <size>` - Viewport size (e.g., 1280x720)
