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

### Stability Tuning (New in this version)
- `HEALTH_CHECK_TIMEOUT` - Timeout for page health checks in seconds (default: `10.0`, increased from `5.0`)
- `CONTENT_EVAL_TIMEOUT` - Timeout for content evaluation in seconds (default: `20.0`, increased from `10.0`)
- `SCRIPT_EVAL_TIMEOUT` - Timeout for JavaScript execution in seconds (default: `60.0`, increased from `30.0`)

**Note**: If you experience "this isn't working right now" errors, try increasing these timeouts:
```bash
export HEALTH_CHECK_TIMEOUT=15.0
export CONTENT_EVAL_TIMEOUT=30.0
export SCRIPT_EVAL_TIMEOUT=90.0
```

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
3. **Page Health Checks**: Atomic health checks with timeout protection (10s, increased from 5s)
4. **JavaScript Evaluation**: All evaluations now have timeout protection (20-60s, increased from 10-30s)
5. **Error Recovery**: Improved recovery that handles browser-level failures
6. **Concurrency**: Safe concurrent operations - multiple tools can run simultaneously
7. **Better Logging**: Added debug/warning logs for health check failures
8. **Enhanced Status Tool**: `get_page_status()` now provides detailed diagnostics and recovery recommendations

### Testing
The server includes extensive tests:
- Concurrent operations (multiple simultaneous calls)
- Error recovery scenarios
- Page health monitoring
- Rapid sequential operations
- Browser restart after close

All 18 tests pass consistently, validating the robustness improvements.

## Troubleshooting

### "This isn't working right now" Error in Claude Desktop

This error typically indicates the MCP server is not responding in time. Common causes and solutions:

1. **Page Health Check Timeout**: The page is taking too long to respond to health checks
   - **Solution**: Increase `HEALTH_CHECK_TIMEOUT` environment variable
   - Add to your MCP config: `"env": { "HEALTH_CHECK_TIMEOUT": "15.0" }`

2. **Long-running Operations**: JavaScript evaluation or content retrieval is timing out
   - **Solution**: Increase `CONTENT_EVAL_TIMEOUT` or `SCRIPT_EVAL_TIMEOUT`
   - For heavy pages: `"env": { "CONTENT_EVAL_TIMEOUT": "30.0", "SCRIPT_EVAL_TIMEOUT": "90.0" }`

3. **Browser in Bad State**: The browser page crashed or became unresponsive
   - **Solution**: Use the `get_page_status()` tool to check health
   - If unhealthy, use `force_reset()` or `close_browser()` to recover

4. **Resource Exhaustion**: Browser has been running for a long time
   - **Solution**: Periodically use `close_browser()` to clean up and restart

### How to Debug

1. Check server logs at `~/Library/Logs/Claude/mcp-server-browser.log`
2. Use `get_page_status()` tool to diagnose page health
3. Look for timeout warnings in the logs
4. Try `force_reset()` if the page is stuck

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
