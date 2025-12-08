# Claude Development Guidelines

This document contains guidelines for AI assistants working on this codebase.

## Workflow

### Use Git Worktrees for Changes

Always create a new worktree for each branch to keep work isolated:

```bash
git worktree add ../dirname -b branch-name
```

This creates a new working directory outside the main repository, which:
- Keeps your main working directory clean and unmodified
- Allows you to work on multiple features simultaneously
- Makes it easy to switch between tasks without stashing or committing incomplete work

### SSH Authentication

When pushing changes, use the appropriate SSH key:

```bash
eval $(ssh-agent) && ssh-add ~/.ssh/id_ed25519_personal
GIT_SSH_COMMAND="ssh -i ~/.ssh/id_ed25519_personal" git push
```

## Code Principles

### Keep the Codebase Minimum, Clean and Consistent

- Only add code that is necessary for the feature or fix
- Remove unused imports, functions, and dependencies
- Follow existing patterns and conventions in the codebase
- Maintain consistency in:
  - Code style and formatting
  - Naming conventions
  - Project structure
  - Documentation style

### Always Test

- Write tests for new features and bug fixes
- Run the test suite before committing changes
- Ensure all tests pass before creating pull requests
- Update existing tests when modifying functionality

**Testing Guidelines:**
- Tests are located in `tests/` directories within each MCP server package (e.g., `src/xlsx/tests/`)
- Run tests from the server directory: `cd src/<server> && uv run pytest -v`
- Test files follow the `test_*.py` naming convention
- Use `pytest` with `uv run` for consistent dependency management
- For servers requiring special setup (browser, composite), check `.github/workflows/test.yml` for environment variables

### Documentation Standards

Each MCP server must have a README.md with:
- **Features**: Overview of what the server does
- **Tools**: List of available tools with parameters and descriptions
- **Requirements**: Dependencies and prerequisites
- **Installation**: Setup instructions
- **Testing**: How to run tests

### Commit Messages

Follow conventional commits format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `refactor:` for code refactoring
- `test:` for test updates

### Dependency Management

This repository uses `uv` for Python package management:
- Install dependencies: `uv sync --dev`
- Add new dependency: Edit `pyproject.toml` and run `uv sync`
- Each MCP server has its own `pyproject.toml` in `src/<server>/`
