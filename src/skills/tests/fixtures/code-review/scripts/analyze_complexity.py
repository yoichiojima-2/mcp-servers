#!/usr/bin/env python3
"""Analyze code complexity metrics."""

import argparse
import json
import sys


def analyze(code: str, language: str = "python") -> dict:
    """Analyze code complexity metrics."""
    lines = code.strip().split("\n")
    non_empty = [line for line in lines if line.strip()]

    metrics = {
        "total_lines": len(lines),
        "code_lines": len(non_empty),
        "blank_lines": len(lines) - len(non_empty),
        "language": language,
    }

    if language == "python":
        metrics["functions"] = sum(1 for line in lines if line.strip().startswith("def "))
        metrics["classes"] = sum(1 for line in lines if line.strip().startswith("class "))
        metrics["imports"] = sum(1 for line in lines if line.strip().startswith(("import ", "from ")))

    return metrics


def main():
    parser = argparse.ArgumentParser(description="Analyze code complexity")
    parser.add_argument("file", nargs="?", help="File to analyze (or stdin if not provided)")
    parser.add_argument("--language", "-l", default="python", help="Programming language")
    args = parser.parse_args()

    if args.file:
        with open(args.file) as f:
            code = f.read()
    else:
        code = sys.stdin.read()

    result = analyze(code, args.language)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
