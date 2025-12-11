"""Template system for rendering content."""

import json
from typing import Any

import markdown
from jinja2 import Environment, BaseLoader
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer

# Markdown extensions for better rendering
MD_EXTENSIONS = [
    "tables",
    "fenced_code",
    "codehilite",
    "toc",
    "nl2br",
]

# Pygments CSS for syntax highlighting
PYGMENTS_CSS = HtmlFormatter(style="monokai").get_style_defs(".codehilite")

# Base HTML template with styling
BASE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        :root {
            --bg: #1a1a2e;
            --surface: #16213e;
            --text: #eee;
            --text-muted: #888;
            --accent: #0f3460;
            --highlight: #e94560;
        }
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--text);
            background: var(--bg);
            margin: 0;
            padding: 2rem;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
        }
        h1, h2, h3, h4 { color: var(--text); margin-top: 1.5em; }
        h1 { border-bottom: 2px solid var(--highlight); padding-bottom: 0.3em; }
        a { color: var(--highlight); }
        code {
            background: var(--surface);
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-size: 0.9em;
        }
        pre {
            background: var(--surface);
            padding: 1rem;
            border-radius: 8px;
            overflow-x: auto;
        }
        pre code { background: none; padding: 0; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 1rem 0;
        }
        th, td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--accent);
        }
        th { background: var(--surface); }
        tr:hover { background: var(--surface); }
        blockquote {
            border-left: 4px solid var(--highlight);
            margin: 1rem 0;
            padding-left: 1rem;
            color: var(--text-muted);
        }
        {{ extra_css }}
    </style>
</head>
<body>
    <div class="container">
        {{ content }}
    </div>
</body>
</html>
"""

# Report template for data presentation
REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        :root {
            --bg: #0f0f23;
            --surface: #1a1a3e;
            --text: #cccccc;
            --text-bright: #ffffff;
            --accent: #00cc00;
            --accent2: #ffcc00;
            --border: #333366;
        }
        * { box-sizing: border-box; }
        body {
            font-family: 'Source Code Pro', 'Fira Code', monospace;
            background: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 2rem;
            line-height: 1.5;
        }
        .report {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            border-bottom: 2px solid var(--accent);
            padding-bottom: 1rem;
            margin-bottom: 2rem;
        }
        .header h1 {
            color: var(--accent);
            margin: 0;
            font-size: 1.5rem;
        }
        .header .meta {
            color: var(--text);
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }
        .section {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 4px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .section h2 {
            color: var(--accent2);
            margin-top: 0;
            font-size: 1.1rem;
            border-bottom: 1px solid var(--border);
            padding-bottom: 0.5rem;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 0.5rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }
        th {
            color: var(--accent);
            font-weight: normal;
            text-transform: uppercase;
            font-size: 0.8rem;
        }
        tr:hover { background: rgba(0, 204, 0, 0.1); }
        .metric {
            display: inline-block;
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 1rem 1.5rem;
            margin: 0.5rem;
            border-radius: 4px;
        }
        .metric-value {
            font-size: 2rem;
            color: var(--accent);
            font-weight: bold;
        }
        .metric-label {
            font-size: 0.8rem;
            color: var(--text);
            text-transform: uppercase;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }
    </style>
</head>
<body>
    <div class="report">
        <div class="header">
            <h1>{{ title }}</h1>
            <div class="meta">Generated: {{ timestamp }}</div>
        </div>
        {{ content }}
    </div>
</body>
</html>
"""

# Dashboard template for multi-widget layouts
DASHBOARD_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <style>
        :root {
            --bg: #1e1e2e;
            --surface: #313244;
            --text: #cdd6f4;
            --subtext: #a6adc8;
            --blue: #89b4fa;
            --green: #a6e3a1;
            --red: #f38ba8;
            --yellow: #f9e2af;
            --border: #45475a;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
        }
        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1rem;
            padding: 1rem;
        }
        .widget {
            background: var(--surface);
            border-radius: 12px;
            padding: 1.5rem;
            border: 1px solid var(--border);
        }
        .widget-title {
            font-size: 0.9rem;
            color: var(--subtext);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 1rem;
        }
        .widget-value {
            font-size: 2.5rem;
            font-weight: 600;
        }
        .widget-value.blue { color: var(--blue); }
        .widget-value.green { color: var(--green); }
        .widget-value.red { color: var(--red); }
        .widget-value.yellow { color: var(--yellow); }
        .widget-subtitle {
            font-size: 0.85rem;
            color: var(--subtext);
            margin-top: 0.5rem;
        }
        .widget-full { grid-column: 1 / -1; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 0.75rem; text-align: left; }
        th { color: var(--subtext); font-weight: 500; font-size: 0.85rem; }
        td { border-top: 1px solid var(--border); }
        .header {
            background: var(--surface);
            padding: 1rem 1.5rem;
            border-bottom: 1px solid var(--border);
        }
        .header h1 {
            font-size: 1.25rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>{{ title }}</h1>
    </div>
    <div class="dashboard">
        {{ content }}
    </div>
</body>
</html>
"""

# Jinja2 environment
_env = Environment(loader=BaseLoader())


def render_markdown(content: str, title: str = "Preview") -> str:
    """Render markdown content to HTML with styling."""
    md = markdown.Markdown(extensions=MD_EXTENSIONS)
    html_content = md.convert(content)

    template = _env.from_string(BASE_TEMPLATE)
    return template.render(
        title=title,
        content=html_content,
        extra_css=PYGMENTS_CSS,
    )


def render_report(
    data: dict[str, Any] | list[Any],
    title: str = "Report",
    sections: list[dict[str, Any]] | None = None,
) -> str:
    """Render data as a report.

    Args:
        data: Data to display (dict for key-value, list for table)
        title: Report title
        sections: Optional list of sections with 'title' and 'content' keys

    Returns:
        Rendered HTML report
    """
    from datetime import datetime

    content_parts = []

    # Handle direct data
    if isinstance(data, dict):
        # Render as metrics grid
        metrics_html = '<div class="grid">'
        for key, value in data.items():
            metrics_html += f"""
            <div class="metric">
                <div class="metric-value">{value}</div>
                <div class="metric-label">{key}</div>
            </div>
            """
        metrics_html += "</div>"
        content_parts.append(f'<div class="section">{metrics_html}</div>')

    elif isinstance(data, list) and data:
        # Render as table
        if isinstance(data[0], dict):
            headers = list(data[0].keys())
            table_html = "<table><thead><tr>"
            for h in headers:
                table_html += f"<th>{h}</th>"
            table_html += "</tr></thead><tbody>"
            for row in data:
                table_html += "<tr>"
                for h in headers:
                    table_html += f"<td>{row.get(h, '')}</td>"
                table_html += "</tr>"
            table_html += "</tbody></table>"
            content_parts.append(f'<div class="section"><h2>Data</h2>{table_html}</div>')

    # Handle sections
    if sections:
        for section in sections:
            section_title = section.get("title", "Section")
            section_content = section.get("content", "")
            if isinstance(section_content, (dict, list)):
                section_content = f"<pre>{json.dumps(section_content, indent=2)}</pre>"
            content_parts.append(f'<div class="section"><h2>{section_title}</h2>{section_content}</div>')

    template = _env.from_string(REPORT_TEMPLATE)
    return template.render(
        title=title,
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        content="\n".join(content_parts),
    )


def render_dashboard(
    widgets: list[dict[str, Any]],
    title: str = "Dashboard",
) -> str:
    """Render a dashboard with widgets.

    Args:
        widgets: List of widget definitions with keys:
            - title: Widget title
            - value: Main value to display
            - subtitle: Optional subtitle
            - color: Optional color (blue, green, red, yellow)
            - full: Optional boolean for full-width widget
            - type: Optional 'table' for table widgets
            - data: For table type, list of dicts

    Returns:
        Rendered HTML dashboard
    """
    widget_parts = []

    for widget in widgets:
        widget_type = widget.get("type", "metric")
        full_class = " widget-full" if widget.get("full") else ""

        if widget_type == "table" and "data" in widget:
            # Table widget
            data = widget["data"]
            if data and isinstance(data[0], dict):
                headers = list(data[0].keys())
                table_html = "<table><thead><tr>"
                for h in headers:
                    table_html += f"<th>{h}</th>"
                table_html += "</tr></thead><tbody>"
                for row in data:
                    table_html += "<tr>"
                    for h in headers:
                        table_html += f"<td>{row.get(h, '')}</td>"
                    table_html += "</tr>"
                table_html += "</tbody></table>"

                widget_parts.append(f"""
                <div class="widget{full_class}">
                    <div class="widget-title">{widget.get("title", "")}</div>
                    {table_html}
                </div>
                """)
        else:
            # Metric widget
            color_class = widget.get("color", "blue")
            widget_parts.append(f"""
            <div class="widget{full_class}">
                <div class="widget-title">{widget.get("title", "")}</div>
                <div class="widget-value {color_class}">{widget.get("value", "")}</div>
                <div class="widget-subtitle">{widget.get("subtitle", "")}</div>
            </div>
            """)

    template = _env.from_string(DASHBOARD_TEMPLATE)
    return template.render(
        title=title,
        content="\n".join(widget_parts),
    )


def highlight_code(code: str, language: str | None = None) -> str:
    """Syntax highlight code.

    Args:
        code: Source code to highlight
        language: Language name (optional, will guess if not provided)

    Returns:
        HTML with syntax highlighting
    """
    try:
        if language:
            lexer = get_lexer_by_name(language)
        else:
            lexer = guess_lexer(code)
    except Exception:
        # Fallback to plain text
        return f"<pre><code>{code}</code></pre>"

    formatter = HtmlFormatter(style="monokai", noclasses=True)
    return highlight(code, lexer, formatter)
