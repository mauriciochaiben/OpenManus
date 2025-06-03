# Pre-commit Hooks Setup for OpenManus

This document describes the comprehensive pre-commit configuration for the OpenManus project, which enforces code quality for both the Python backend and React/TypeScript frontend.

## Overview

The `.pre-commit-config.yaml` file configures automated checks that run before each commit, ensuring consistent code quality across the entire codebase.

## Installation & Setup

1. **Install pre-commit** (if not already installed):
   ```bash
   pip install pre-commit
   ```

2. **Install the git hook scripts**:
   ```bash
   pre-commit install
   ```

3. **Install commit message hook** (optional):
   ```bash
   pre-commit install --hook-type commit-msg
   ```

## Configured Hooks

### Basic File Hygiene
- **check-yaml**: Validates YAML syntax
- **check-json**: Validates JSON syntax
- **check-toml**: Validates TOML syntax
- **end-of-file-fixer**: Ensures files end with newline
- **trailing-whitespace**: Removes trailing whitespace
- **check-merge-conflict**: Detects merge conflict markers
- **check-added-large-files**: Prevents large files (>500KB)
- **check-case-conflict**: Detects case-sensitive naming conflicts

### Python Backend (app/, tests/, scripts/, demos/, examples/)
- **Ruff Linter**: Fast Python linter (replaces flake8, isort, etc.)
- **Ruff Formatter**: Code formatting (replaces black)
- **MyPy**: Static type checking with project-specific configuration
- **Bandit**: Security vulnerability scanning
- **Hadolint**: Dockerfile linting

### Frontend (frontend/src/)
- **ESLint**: TypeScript/React linting with comprehensive rules:
  - TypeScript strict checking
  - React best practices
  - Accessibility (jsx-a11y)
  - Import organization
  - React Hooks rules
- **Prettier**: Code formatting with project configuration
- **TypeScript Check**: Type checking without emission (`tsc --noEmit`)

### Additional Tools
- **Commitizen**: Enforces conventional commit message format

## File Patterns

### Python Files
```
^(app/|tests/|scripts/|demos/|examples/|.*\.py)$
```

### Frontend Files
```
^frontend/src/.*\.(ts|tsx|js|jsx)$  # ESLint
^frontend/.*\.(js|ts|jsx|tsx|css|scss|json|html|md)$  # Prettier
```

## Running Hooks Manually

### Run all hooks on all files:
```bash
pre-commit run --all-files
```

### Run specific hook:
```bash
pre-commit run ruff --all-files
pre-commit run eslint --all-files
pre-commit run prettier --all-files
```

### Run hooks on specific files:
```bash
pre-commit run --files app/main.py
pre-commit run --files frontend/src/App.tsx
```

## Configuration Details

### ESLint Configuration
- Uses project-specific `.eslintrc.cjs` in frontend/
- Includes React, TypeScript, accessibility, and testing plugins
- Auto-fixes issues when possible

### Prettier Configuration
- Uses project-specific `.prettierrc` in frontend/
- Consistent formatting across all frontend files

### MyPy Configuration
- Uses `pyproject.toml` for configuration
- Includes type stubs for common libraries (requests, PyYAML, etc.)

### Ruff Configuration
- Replaces black, flake8, isort, and other Python tools
- Fast and comprehensive Python linting and formatting

## Performance Settings

- **Python**: 3.12
- **Node**: 20.11.0
- **Fail Fast**: Disabled (runs all hooks even if one fails)
- **Minimum pre-commit version**: 3.0.0

## Excluded Patterns

The configuration excludes common build artifacts and dependencies:
- `node_modules/`, `dist/`, `build/`, `coverage/`
- `__pycache__/`, `.pytest_cache/`, `.mypy_cache/`
- `.git/`, `.venv/`, `venv/`
- `logs/`, `workspace/`, `uploads/`
- Minified files (`.min.js`, `.min.css`)

## Troubleshooting

### Hook Fails
1. Read the error message carefully
2. Fix the issues manually or let auto-fix handle them
3. Re-run the commit

### Skip Hooks (Emergency)
```bash
git commit --no-verify -m "emergency fix"
```

### Update Hook Versions
```bash
pre-commit autoupdate
```

### Clear Cache
```bash
pre-commit clean
```

## Integration with CI/CD

The same hooks can be run in CI/CD pipelines:
```bash
pre-commit run --all-files --show-diff-on-failure
```

This ensures the same quality standards are enforced both locally and in automated builds.
