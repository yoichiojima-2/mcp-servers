# Claude Development Guidelines

This document contains guidelines for AI assistants working on this codebase.

## Workflow

### GitHub Flow

This repository follows [GitHub Flow](https://guides.github.com/introduction/flow/), a lightweight, branch-based workflow:

1. **Main branch is always deployable**: The `main` branch should always be in a working state
2. **Create descriptive branches**: Create a new branch off `main` for each feature or fix
   - Use descriptive names: `feat/add-feature`, `fix/bug-description`, `docs/update-readme`
3. **Commit often**: Make small, focused commits with clear messages
4. **Open a Pull Request**: Open a PR early to start discussion and get feedback
5. **Review and discuss**: Collaborate on code review and address feedback
6. **Merge to main**: Once approved and tests pass, merge the PR to `main`

**Branch Naming Convention:**
- `feat/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test updates

### Claude Code Review Workflow

After creating a PR, CI workflows will automatically run (typically completes within a few minutes). **You must wait for the review to complete and address any issues it identifies.**

**Note**: Multiple workflows run on PRs:
- **Run Tests**: Validates code with pytest across all MCP servers
- **Claude Code Review**: Provides automated code review feedback

Both should complete successfully before merging.

**Process:**
1. After running `gh pr create`, wait for the CI workflows to complete
2. Check the review status with: `gh pr checks` or `gh run list --limit 5`
3. Once complete, view the review results: `gh run view <run-id>`
4. If issues are found, fix them and push updates to the PR branch
5. Repeat until the review passes

**Commands to monitor and address CI review:**
```bash
# Check all workflow runs for the current PR (preferred)
gh pr checks

# Or specify a PR number
gh pr checks <pr-number>

# List recent workflow runs
gh run list --limit 5

# List Claude Code Review runs for the PR (run from PR branch directory)
gh run list --workflow=claude-code-review.yml --branch=$(git branch --show-current) --limit 5

# View details of a specific run (get run-id from the list above)
gh run view <run-id>

# View failed job logs
gh run view <run-id> --log-failed

# After fixing issues, commit and push
git add . && git commit -m "fix: address review feedback" && git push
```

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

If you need to use a specific SSH key for authentication:

```bash
# Add your SSH key to the agent
eval $(ssh-agent) && ssh-add ~/.ssh/your_key_name

# Push using the specific key
GIT_SSH_COMMAND="ssh -i ~/.ssh/your_key_name" git push
```

Replace `your_key_name` with your actual SSH key filename (e.g., `id_ed25519`, `id_rsa`).

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

**E2E Testing with Claude Desktop:**
- Claude Desktop MCP settings path: `~/Library/Application Support/Claude`
- Claude Desktop logs path: `~/Library/Logs/Claude`
- Use this path when testing MCP servers with Claude Code or Claude Desktop integration

### Linting and Formatting

Always run ruff to check and format code before committing:

```bash
# Fix linting issues automatically
uv run ruff check --fix

# Format code
uv run ruff format
```

Run these commands from the repository root to check the entire codebase.

### Skills Reference

For Claude Code skills examples, see [anthropic/skills](https://github.com/anthropics/skills)

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

### Adding New MCP Servers

When adding a new MCP server to the workspace:

1. Create the server directory structure under `src/<server-name>/`
2. Add the server to the workspace members in root `pyproject.toml`
3. Add the server to `.github/workflows/test.yml` matrix to ensure CI runs tests
4. If the server should be available in composite, add it to:
   - `src/composite/pyproject.toml` dependencies and `[tool.uv.sources]`
   - `src/composite/composite-config.yaml` with appropriate settings

### Port Assignment

Default ports are assigned alphabetically, with composite reserved at 8000:

- **composite**: 8000 (reserved for the aggregator server)
- **Other servers**: 8001-8013, assigned alphabetically by server name

When adding a new server, assign the next available port after the last alphabetically-sorted server. See `docs/server-guide.md` for the current port assignments.

### Consistency Rules

When modifying MCP servers, ensure these files stay in sync:

| File | What to update |
|------|----------------|
| `src/<server>/src/<module>/server.py` | `DEFAULT_PORT` constant |
| `src/<server>/docker-compose.yml` | `ports` mapping and `PORT` env var |
| `src/composite/docker-compose.yml` | Backend service definition and `PORT` env var |
| `src/composite/composite-config.yaml` | Server entry with `enabled`, `prefix`, `module` |
| `docs/server-guide.md` | Server Reference table |

When adding a new server, update all of these. When changing ports, update all of these.

### Dependency Management

This repository uses a **Google-style monorepo** with `uv` workspaces for unified dependency management:

**Structure:**
- Root `pyproject.toml` contains global dependencies shared across all servers (fastmcp, python-dotenv, uvicorn, pytest, ruff, etc.)
- Each server's `pyproject.toml` in `src/<server>/` only declares server-specific dependencies
- Single `uv.lock` file at the root manages all dependencies across the workspace

**Common Commands:**
- Install all dependencies: `uv sync --dev` (run from root)
- Add global dependency: Edit root `pyproject.toml`, then run `uv lock && uv sync --dev`
- Add server-specific dependency: Edit `src/<server>/pyproject.toml`, then run `uv lock && uv sync --dev`
- Run server: `cd src/<server> && uv run fastmcp run server.py`
- Run tests: `cd src/<server> && uv run pytest -v`

**Benefits:**
- Shared dependencies are defined once at the root
- Single lock file ensures consistent versions across all servers
- Easier dependency updates and version management
- Follows Google monorepo best practices
