---
name: code-review
description: |
  Review code for quality, bugs, security issues, and best practices.
  Use this skill when the user asks for code review, code analysis, or wants feedback on their code.
---

# Code Review Skill

This skill helps you perform thorough code reviews.

## Guidelines

When reviewing code, check for:
1. **Correctness** - Does the code do what it's supposed to?
2. **Security** - Are there any vulnerabilities?
3. **Performance** - Are there obvious inefficiencies?
4. **Readability** - Is the code clear and maintainable?
5. **Best Practices** - Does it follow language conventions?

## Available Scripts

Run these from the skill's base_path:

```bash
# Analyze code complexity
python scripts/analyze_complexity.py <file>
# or via stdin
cat <file> | python scripts/analyze_complexity.py

# Check code style
python scripts/check_style.py <file>
# or via stdin
cat <file> | python scripts/check_style.py
```

## Usage

1. Run `analyze_complexity.py` to get metrics
2. Run `check_style.py` for style issues
3. Provide comprehensive feedback based on the results
