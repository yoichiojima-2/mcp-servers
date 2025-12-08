# Claude Code Development Guide

## Git Worktree Setup

Before making any code edits, create a git worktree. This is essential because:

1. Agents will apply fixes concurrently
2. Multiple agents can work on different branches simultaneously without conflicts
3. It allows for parallel development and testing

### Creating a Git Worktree

```bash
# Create a new worktree for a feature branch
git worktree add ../mcp-servers-feature-name feature-name

# Or create worktree with a new branch
git worktree add -b feature-name ../mcp-servers-feature-name

# List existing worktrees
git worktree list

# Remove a worktree when done
git worktree remove ../mcp-servers-feature-name
```

### Workflow

1. **Before starting work**: Create a worktree for your feature/fix
2. **During development**: Multiple agents can work in separate worktrees
3. **After completion**: Merge the branch and remove the worktree

This approach ensures clean separation of concerns and prevents conflicts when agents work concurrently.
