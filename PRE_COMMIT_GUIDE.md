# Pre-commit Setup Guide

This document explains how to set up and use pre-commit hooks for the OpenManus project.

## What is Pre-commit?

Pre-commit is a framework for managing and maintaining multi-language pre-commit hooks. It automatically runs code quality checks and formatting before each commit, helping maintain consistent code standards across the project.

## Installation

Pre-commit is already configured for this project. To set it up:

1. **Install pre-commit** (if not already installed):
   ```bash
   pip install pre-commit
   ```

2. **Install the hooks**:
   ```bash
   pre-commit install
   ```

3. **Optional: Install commit-msg hook for conventional commits**:
   ```bash
   pre-commit install --hook-type commit-msg
   ```

## Configured Hooks

### Python Backend (`app/`, `tests/`, `scripts/`)

- **Ruff Linter**: Comprehensive Python linting (replaces flake8, isort, and more)
- **Ruff Formatter**: Code formatting (replaces black)
- **MyPy**: Static type checking
- **Bandit**: Security vulnerability scanner

### Frontend (`frontend/`)

- **Prettier**: Code formatting for JS/TS/CSS/HTML/JSON
- **ESLint**: JavaScript/TypeScript linting

### General

- **YAML/JSON/TOML validation**: Syntax checking
- **Trailing whitespace**: Removes trailing spaces
- **End of file fixer**: Ensures files end with newline
- **Large file check**: Prevents committing files > 500KB
- **Merge conflict detection**: Checks for merge conflict markers
- **Dockerfile linting**: Hadolint for Dockerfile best practices

### Security & Quality

- **Bandit**: Python security linter
- **Commitizen**: Enforces conventional commit messages

## Usage

### Automatic Execution

Once installed, hooks run automatically on every commit:

```bash
git add .
git commit -m "your commit message"
# Pre-commit hooks will run automatically
```

### Manual Execution

Run hooks manually on all files:
```bash
pre-commit run --all-files
```

Run a specific hook:
```bash
pre-commit run ruff --all-files
pre-commit run prettier --all-files
pre-commit run mypy --all-files
```

Run hooks on specific files:
```bash
pre-commit run --files app/llm.py
pre-commit run --files frontend/src/components/Chat.vue
```

### Skip Hooks (Emergency Only)

To bypass hooks in emergency situations:
```bash
git commit --no-verify -m "emergency commit"
```

⚠️ **Use sparingly** - this should only be used in true emergencies.

## Configuration Files

- **`.pre-commit-config.yaml`**: Main configuration
- **`pyproject.toml`**: Contains Ruff and other Python tool settings
- **`frontend/.eslintrc.js`**: ESLint configuration (if exists)
- **`frontend/.prettierrc`**: Prettier configuration (if exists)

## Troubleshooting

### Hook Installation Issues

If you encounter Python version issues:
```bash
pre-commit clean
pre-commit install
```

### Updating Hooks

Update to latest hook versions:
```bash
pre-commit autoupdate
```

### Performance Issues

Skip slow hooks during development:
```bash
# Skip mypy for faster commits during development
SKIP=mypy git commit -m "your message"
```

### Frontend Dependency Issues

If ESLint or Prettier fail due to missing dependencies:
```bash
cd frontend
npm install
```

## Integration with IDEs

### VS Code

Install these extensions for better integration:
- **Ruff**: `charliermarsh.ruff`
- **Prettier**: `esbenp.prettier-vscode`
- **ESLint**: `dbaeumer.vscode-eslint`
- **MyPy**: `ms-python.mypy-type-checker`

### PyCharm/IntelliJ

- Enable Ruff in Settings → Tools → External Tools
- Configure Prettier for frontend files
- Enable MyPy type checking

## Continuous Integration

Pre-commit hooks should also be run in CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run pre-commit
  uses: pre-commit/action@v3.0.0
```

## Best Practices

1. **Fix issues locally**: Don't push commits that fail pre-commit hooks
2. **Keep hooks fast**: Avoid adding slow hooks that block development
3. **Update regularly**: Run `pre-commit autoupdate` monthly
4. **Document exceptions**: If you need to skip a hook, document why
5. **Team adoption**: Ensure all team members install pre-commit

## Common Commands

```bash
# Initial setup
pre-commit install

# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff

# Update hook versions
pre-commit autoupdate

# Clean cache (if issues)
pre-commit clean

# Uninstall hooks
pre-commit uninstall
```

## Hook-Specific Notes

### Ruff
- Configured to fix issues automatically where possible
- Uses settings from `pyproject.toml`
- Replaces multiple tools (black, flake8, isort, etc.)

### MyPy
- Only runs on `app/` directory
- Configured to ignore missing imports
- May need additional type stubs for some packages

### Prettier
- Formats frontend code automatically
- Uses project-specific configuration if available

### ESLint
- Lints JavaScript/TypeScript in frontend
- Configured with TypeScript and Vue support

## Support

If you encounter issues with pre-commit hooks:

1. Check this documentation
2. Try cleaning cache: `pre-commit clean`
3. Update hooks: `pre-commit autoupdate`
4. Ask the team for help

Remember: These tools are here to help maintain code quality, not to slow you down. If a hook is consistently problematic, we can adjust the configuration.
