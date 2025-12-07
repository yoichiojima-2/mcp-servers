# browser

A robust MCP server that allows clients to manipulate browser using Playwright with automatic error handling and recovery.

## Installation

```bash
make install
```

## Usage

```bash
make serve
```

## Environment Variables

- `HEADLESS` - Run browser in headless mode (default: `false`)
- `BROWSER_TIMEOUT` - Default timeout for browser operations in ms (default: `30000`)
- `NAVIGATION_TIMEOUT` - Timeout for page navigation in ms (default: `60000`)
- `WORKSPACE` - Directory for screenshots (default: `workspace`)
- `NO_SANDBOX` - Disable browser sandbox (default: `false`, use with caution)
- `TRANSPORT` - Transport protocol (default: `stdio`)
- `NAME` - MCP server name (default: `browser`)

## Features

### Concurrency Safety
- Thread-safe operations with async locks
- No race conditions during concurrent tool calls
- Event loop-aware lock management
- Safe concurrent page access

### Automatic Error Handling
- All tools automatically catch and recover from errors
- Page health checks detect crashed or unresponsive pages
- Automatic page reset when errors occur
- Graceful timeout handling
- Recovery from browser-level failures

### Resource Management
- Memory limits to prevent browser crashes
- Configurable timeouts for all operations
- Automatic cleanup of resources
- Timeout protection on JavaScript evaluation

### Browser State Management
- Page health monitoring with timeout protection
- Automatic recovery from crashed states
- Force reset capability
- Atomic health checks and page retrieval

## Tools

### Navigation
- `navigate(url)` - Navigate to a URL with automatic timeout handling
- `go_back()` - Go back to the previous page
- `go_forward()` - Go forward to the next page
- `reload()` - Reload the current page

### Content
- `get_content(max_length=10000)` - Get text content (handles large pages)
- `get_url()` - Get the current page URL
- `get_title()` - Get the current page title

### Interaction
- `click(selector)` - Click an element by CSS selector
- `fill(selector, value)` - Fill a form field
- `type_text(selector, text)` - Type text (simulates real typing)
- `press_key(key)` - Press a keyboard key
- `select_option(selector, value)` - Select dropdown option
- `hover(selector)` - Hover over an element

### Screenshots
- `screenshot(filename, full_page)` - Save screenshot to file
- `screenshot_base64(full_page)` - Get screenshot as base64

### JavaScript
- `evaluate(script)` - Execute JavaScript in the browser

### Wait Functions
- `wait_for_selector(selector, timeout)` - Wait for element to appear
- `wait_for_navigation(timeout)` - Wait for navigation to complete

### Browser Management
- `close_browser()` - Close browser and cleanup resources
- `force_reset()` - Force reset the page if in bad state
- `get_page_status()` - Check if page is healthy

## Robustness Improvements

This version includes comprehensive fixes to eliminate flakiness:

### Fixed Issues
1. **Race Conditions**: Added async locks to prevent concurrent access issues
2. **Event Loop Compatibility**: Locks are now event loop-aware, preventing "bound to different event loop" errors
3. **Page Health Checks**: Atomic health checks with timeout protection (5s)
4. **JavaScript Evaluation**: All evaluations now have timeout protection (10-30s)
5. **Error Recovery**: Improved recovery that handles browser-level failures
6. **Concurrency**: Safe concurrent operations - multiple tools can run simultaneously

### Testing
The server includes extensive tests:
- Concurrent operations (multiple simultaneous calls)
- Error recovery scenarios
- Page health monitoring
- Rapid sequential operations
- Browser restart after close

All 18 tests pass consistently, validating the robustness improvements.

## Troubleshooting

### "No compatible message available" Error
This error occurs when the browser page crashes or becomes unresponsive. The improvements in this version handle this automatically by:

1. Detecting page health before operations with timeout protection
2. Automatically resetting crashed pages
3. Providing `force_reset()` tool for manual recovery
4. Safe recovery even during concurrent operations

### Large Pages (like Reddit)
For content-heavy sites:
- Use `get_content(max_length=...)` to control output size
- Content is automatically truncated with total length reported
- Consider using `evaluate()` to extract specific data instead of full page content

### Example: Extract Specific Content
```javascript
// Instead of get_content(), use evaluate() to get only what you need
evaluate(`
  Array.from(document.querySelectorAll('h1, h2, h3'))
    .map(el => el.textContent)
    .join('\\n')
`)
```

### Concurrent Operations
The server now safely handles multiple concurrent tool calls:
- Operations are serialized with async locks
- No race conditions or state corruption
- Safe for parallel workflows
