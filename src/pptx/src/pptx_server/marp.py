"""
Marp-based Markdown to PPTX conversion.

This module provides high-quality presentation generation using Marp CLI
with distinctive, professionally-designed CSS themes from the frontend-design
package.

Requires: Node.js v18+ and a browser (Chrome, Edge, or Firefox)
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from frontend_design.themes import THEMES, get_theme

from . import mcp

# Constants
MAX_MARKDOWN_SIZE = 10_000_000  # 10MB limit for markdown content
MARP_TIMEOUT = 60  # Seconds timeout for marp-cli conversion
FORBIDDEN_PATHS = frozenset(["/bin", "/sbin", "/usr", "/etc", "/sys", "/proc", "/var", "/root"])


def _check_marp_cli() -> bool:
    """Check if marp-cli is available."""
    try:
        result = subprocess.run(
            ["npx", "@marp-team/marp-cli", "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def _check_browser() -> bool:
    """Check if a supported browser is available for PPTX conversion."""
    browsers = [
        # Cross-platform (via PATH)
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        shutil.which("chrome"),
        shutil.which("firefox"),
        shutil.which("msedge"),
        # macOS paths
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        "/Applications/Firefox.app/Contents/MacOS/firefox",
    ]
    # Windows paths
    if os.name == "nt":
        browsers.extend(
            [
                os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
                os.path.expandvars(r"%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"),
                os.path.expandvars(r"%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"),
                os.path.expandvars(r"%ProgramFiles%\Mozilla Firefox\firefox.exe"),
                os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
            ]
        )
    return any(b and Path(b).exists() for b in browsers if b)


def _validate_output_path(path: Path) -> None:
    """Validate output path is safe to write to."""
    path_str = str(path)
    # Check for forbidden system directories
    for forbidden in FORBIDDEN_PATHS:
        if path_str.startswith(forbidden):
            raise ValueError(f"Cannot write to system directory: {forbidden}")
    # Ensure parent directory exists or can be created
    if not path.parent.exists():
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise ValueError(f"Permission denied: cannot create {path.parent}")


def convert_markdown_to_pptx(
    markdown_content: str,
    output_path: str,
    theme: str = "minimal",
) -> str:
    """
    Convert Marp-formatted Markdown to PPTX using marp-cli.

    Args:
        markdown_content: Markdown content with Marp frontmatter
        output_path: Path for the output PPTX file
        theme: Theme name from available themes

    Returns:
        Path to the created PPTX file
    """
    # Validate inputs
    if len(markdown_content) > MAX_MARKDOWN_SIZE:
        raise ValueError(f"Markdown content too large (max {MAX_MARKDOWN_SIZE // 1_000_000}MB)")

    if theme not in THEMES:
        raise ValueError(f"Unknown theme: {theme}. Available: {list(THEMES.keys())}")

    output_path = Path(output_path).expanduser().resolve()
    _validate_output_path(output_path)

    theme_data = get_theme(theme)
    theme_css = theme_data.get("marp_css", "")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Write theme CSS
        theme_path = tmpdir / f"{theme}.css"
        theme_path.write_text(theme_css)

        # Prepare markdown with theme reference
        if not markdown_content.strip().startswith("---"):
            markdown_content = f"""---
marp: true
theme: {theme}
paginate: true
---

{markdown_content}"""
        else:
            # Inject theme into existing frontmatter
            lines = markdown_content.split("\n")
            frontmatter_end = -1
            for i, line in enumerate(lines[1:], 1):
                if line.strip() == "---":
                    frontmatter_end = i
                    break

            if frontmatter_end > 0:
                has_theme = any("theme:" in line for line in lines[1:frontmatter_end])
                if not has_theme:
                    lines.insert(frontmatter_end, f"theme: {theme}")
                markdown_content = "\n".join(lines)

        # Write markdown file
        md_path = tmpdir / "slides.md"
        md_path.write_text(markdown_content)

        # Run marp-cli
        cmd = [
            "npx",
            "@marp-team/marp-cli",
            str(md_path),
            "--pptx",
            "--theme",
            str(theme_path),
            "--allow-local-files",
            "-o",
            str(output_path),
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=MARP_TIMEOUT,
                cwd=tmpdir,
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                raise RuntimeError(f"Marp conversion failed: {error_msg}")

        except subprocess.TimeoutExpired:
            raise RuntimeError(f"Marp conversion timed out after {MARP_TIMEOUT} seconds")
        except FileNotFoundError:
            raise RuntimeError("npx not found. Please install Node.js v18+ to use Marp. Visit: https://nodejs.org/")

    if not output_path.exists():
        raise RuntimeError(f"PPTX file was not created: {output_path}")

    return str(output_path)


# ======================================================
# MCP Tools
# ======================================================


# Note: Theme listing is provided by frontend-design server via design_list_themes()


@mcp.tool()
def marp_create_presentation(
    markdown: str,
    output_path: str,
    theme: str = "minimal",
) -> str:
    """
    Create a professionally-designed PPTX from Markdown using Marp.

    Uses distinctive themes that avoid generic AI aesthetics.
    Each theme has bold, intentional design choices.

    Args:
        markdown: Marp-formatted Markdown content. Use '---' to separate slides.
                  Supports: headings, lists, code blocks, tables, images, blockquotes.
                  Use '<!-- _class: lead -->' for title slides.
                  Use '<!-- _class: invert -->' for accent/inverted slides.
        output_path: Path for the output PPTX file
        theme: Theme name - one of: noir, brutalist, organic, neon, minimal, retro

    Returns:
        Path to the created PPTX file

    Example markdown:
        ---
        marp: true
        ---

        <!-- _class: lead -->
        # My Presentation
        Subtitle goes here

        ---

        ## First Topic

        - Key point one
        - Key point two
        - Key point three

        ---

        <!-- _class: invert -->
        ## Questions?

        Contact: email@example.com
    """
    try:
        result_path = convert_markdown_to_pptx(markdown, output_path, theme)
        theme_data = get_theme(theme)
        return f"Created presentation: {result_path}\nTheme: {theme_data['name']}"
    except Exception as e:
        return f"Error creating presentation: {e}"


@mcp.tool()
def marp_create_presentation_from_file(
    markdown_file: str,
    output_path: str,
    theme: str = "minimal",
) -> str:
    """
    Create a PPTX from a Markdown file using Marp.

    Args:
        markdown_file: Path to the Markdown file
        output_path: Path for the output PPTX file
        theme: Theme name - one of: noir, brutalist, organic, neon, minimal, retro

    Returns:
        Path to the created PPTX file
    """
    md_path = Path(markdown_file).expanduser().resolve()

    if not md_path.exists():
        return f"Error: Markdown file not found: {md_path}"

    markdown_content = md_path.read_text()

    try:
        result_path = convert_markdown_to_pptx(markdown_content, output_path, theme)
        theme_data = get_theme(theme)
        return f"Created presentation: {result_path}\nTheme: {theme_data['name']}"
    except Exception as e:
        return f"Error creating presentation: {e}"


@mcp.tool()
def marp_check_requirements() -> str:
    """
    Check if Marp CLI requirements are met.

    Marp requires:
    - Node.js v18 or later
    - A browser (Chrome, Edge, or Firefox) for PPTX export

    Returns:
        Status of requirements
    """
    results = []

    # Check Node.js
    try:
        node_result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if node_result.returncode == 0:
            version = node_result.stdout.strip()
            results.append(f"✓ Node.js: {version}")
        else:
            results.append("✗ Node.js: Not found")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        results.append("✗ Node.js: Not found")

    # Check npx
    try:
        npx_result = subprocess.run(
            ["npx", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if npx_result.returncode == 0:
            results.append(f"✓ npx: {npx_result.stdout.strip()}")
        else:
            results.append("✗ npx: Not found")
    except (subprocess.TimeoutExpired, FileNotFoundError):
        results.append("✗ npx: Not found")

    # Check marp-cli
    if _check_marp_cli():
        results.append("✓ marp-cli: Available (via npx)")
    else:
        results.append("✗ marp-cli: Will be installed on first use")

    # Check browser
    if _check_browser():
        results.append("✓ Browser: Found (required for PPTX export)")
    else:
        results.append("✗ Browser: Not found (Chrome, Edge, or Firefox needed for PPTX)")

    results.append("\n---")
    results.append("To install Node.js: https://nodejs.org/")
    results.append("Marp CLI is installed automatically via npx on first use.")

    return "\n".join(results)


# Note: Theme CSS is provided by frontend-design server via design_get_theme()
