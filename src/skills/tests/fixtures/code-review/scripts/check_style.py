#!/usr/bin/env python3
"""Check code for style issues."""

import argparse
import json
import sys


def check(code: str, language: str = "python") -> list[dict]:
    """Check code for style issues."""
    issues = []
    lines = code.split("\n")

    for i, line in enumerate(lines, 1):
        if len(line) > 120:
            issues.append(
                {"line": i, "issue": "line_too_long", "message": f"Line exceeds 120 characters ({len(line)})"}
            )

        if line != line.rstrip():
            issues.append({"line": i, "issue": "trailing_whitespace", "message": "Trailing whitespace"})

        if language == "python" and "\t" in line:
            issues.append({"line": i, "issue": "tabs", "message": "Use spaces instead of tabs"})

    return issues


def main():
    parser = argparse.ArgumentParser(description="Check code style")
    parser.add_argument("file", nargs="?", help="File to check (or stdin if not provided)")
    parser.add_argument("--language", "-l", default="python", help="Programming language")
    args = parser.parse_args()

    if args.file:
        with open(args.file) as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = check(code, args.language)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
