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

This repository uses a **Google-style monorepo** with `uv` workspaces for unified dependency management:

**Structure:**
- Root `pyproject.toml` contains global dependencies shared across all servers (fastmcp, python-dotenv, uvicorn, pytest, ruff, etc.)
- Each server's `pyproject.toml` in `src/<server>/` only declares server-specific dependencies
- Single `uv.lock` file at the root manages all dependencies across the workspace

**Common Commands:**
- Install all dependencies: `uv sync --dev` (run from root)
- Add global dependency: Edit root `pyproject.toml` and run `uv lock`
- Add server-specific dependency: Edit `src/<server>/pyproject.toml` and run `uv lock`
- Run server: `cd src/<server> && uv run fastmcp run server.py`
- Run tests: `cd src/<server> && uv run pytest -v`

**Benefits:**
- Shared dependencies are defined once at the root
- Single lock file ensures consistent versions across all servers
- Easier dependency updates and version management
- Follows Google monorepo best practices
