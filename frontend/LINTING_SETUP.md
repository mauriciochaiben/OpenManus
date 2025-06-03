# ESLint and Prettier Configuration

## Overview

This document describes the comprehensive ESLint and Prettier configuration for the OpenManus frontend React/TypeScript project. The setup enforces code quality, consistency, and best practices across the entire codebase.

## Configuration Files

### `.eslintrc.cjs`

The main ESLint configuration file with the following key features:

- **TypeScript Support**: Uses `@typescript-eslint/parser` and `@typescript-eslint/eslint-plugin` v7.18.0
- **React Integration**: Includes React-specific rules and hooks validation
- **Accessibility**: Enforces accessibility standards with `eslint-plugin-jsx-a11y`
- **Testing**: Supports testing library patterns with `eslint-plugin-testing-library`
- **Code Complexity**: Limits function complexity (max 10), nesting depth (max 4), and nested callbacks (max 3)

### `.prettierrc`

Prettier configuration for consistent code formatting:

- Double quotes for strings
- Semicolons required
- 2-space indentation
- 80 character line width
- Trailing commas in ES5 compatible mode

### VS Code Integration (`.vscode/settings.json`)

Automatic formatting and linting in VS Code:

- Format on save enabled
- ESLint auto-fix on save
- Prettier as default formatter
- TypeScript validation enabled

## Package.json Scripts

```json
{
  "scripts": {
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "lint:fix": "eslint . --ext ts,tsx --fix",
    "format": "prettier --write \"src/**/*.{ts,tsx,js,jsx,json,css,md}\""
  }
}
```

## Pre-commit Hooks

The project uses **Husky** and **lint-staged** to automatically lint and format code before commits:

### Setup

1. Husky is configured in the root `.husky/pre-commit` file
2. lint-staged configuration in `frontend/package.json` runs ESLint and Prettier on staged files
3. Only properly formatted and linted code can be committed

### Configuration

```json
{
  "lint-staged": {
    "*.{ts,tsx}": ["eslint --fix", "prettier --write"],
    "*.{js,jsx}": ["eslint --fix", "prettier --write"],
    "*.{json,css,md}": ["prettier --write"]
  }
}
```

## Usage Guidelines

### Running Linting and Formatting

```bash
# Check for linting errors
npm run lint

# Auto-fix linting errors
npm run lint:fix

# Format code with Prettier
npm run format
```

### IDE Integration

**VS Code (Recommended)**:

1. Install the ESLint extension (`ms-vscode.vscode-eslint`)
2. Install the Prettier extension (`esbenp.prettier-vscode`)
3. The `.vscode/settings.json` file will automatically configure format-on-save

**Other IDEs**:

- Configure your IDE to use the project's ESLint and Prettier configurations
- Enable format-on-save if available

## Rule Categories

### TypeScript Rules

- Strict type checking with `@typescript-eslint/no-explicit-any` warnings
- Consistent import/export patterns
- Proper type annotations
- No unused variables or imports

### React Rules

- Proper key props for array elements
- Hooks dependency validation
- Component naming conventions
- JSX accessibility standards

### Code Quality Rules

- Function complexity limits (max 10)
- Nesting depth limits (max 4)
- Callback nesting limits (max 3)
- Console statement warnings
- Consistent error handling

### Formatting Rules (Prettier)

- 2-space indentation
- 80-character line width
- Double quotes
- Semicolons required
- Trailing commas (ES5)

## Project Status

### Current Metrics

- **Before Setup**: 5,203 ESLint issues
- **After Setup**: 344 warnings, 0 errors
- **Improvement**: 93% reduction in issues

### Remaining Tasks

The 344 remaining warnings are primarily:

- `no-console` statements (can be addressed gradually)
- `@typescript-eslint/no-explicit-any` (replace with proper types)
- Complex functions (refactor for better maintainability)
- Missing dependency array items in hooks

## Best Practices

### For Developers

1. **Before Committing**:

   - Run `npm run lint` to check for issues
   - Run `npm run format` to ensure consistent formatting
   - The pre-commit hook will automatically run these checks

2. **Writing New Code**:

   - Use TypeScript types instead of `any`
   - Keep functions simple (complexity < 10)
   - Add proper `key` props to array elements
   - Follow React hooks dependency rules

3. **Handling Existing Warnings**:
   - Address warnings when working in files
   - Prioritize fixing errors over warnings
   - Use `// eslint-disable-next-line` sparingly and with comments

### For Code Reviews

- Check that new code passes all ESLint rules
- Ensure proper TypeScript typing
- Verify accessibility compliance
- Confirm consistent formatting

## Troubleshooting

### Common Issues

1. **ESLint Parser Errors**:

   - Ensure TypeScript version compatibility
   - Check `tsconfig.json` paths in ESLint config

2. **Prettier Conflicts**:

   - Use `eslint-config-prettier` to disable conflicting ESLint rules
   - Ensure consistent configuration between ESLint and Prettier

3. **Pre-commit Hook Failures**:
   - Run `npm run lint:fix` manually
   - Check file permissions on `.husky/pre-commit`
   - Ensure lint-staged is properly configured

### Configuration Updates

When updating ESLint or TypeScript versions:

1. Check compatibility between `@typescript-eslint` packages and TypeScript version
2. Update both parser and plugin versions together
3. Test the configuration with `npm run lint`
4. Update this documentation if rules change

## Dependencies

### Core Linting Dependencies

- `eslint`: ^8.0.0
- `@typescript-eslint/eslint-plugin`: ^7.18.0
- `@typescript-eslint/parser`: ^7.18.0
- `typescript`: ^5.8.3

### Additional Plugins

- `eslint-plugin-react`: React-specific rules
- `eslint-plugin-react-hooks`: React hooks validation
- `eslint-plugin-jsx-a11y`: Accessibility rules
- `eslint-plugin-testing-library`: Testing best practices

### Formatting Dependencies

- `prettier`: ^3.4.2

### Git Hook Dependencies

- `husky`: ^9.1.7
- `lint-staged`: ^16.1.0

This configuration ensures consistent, high-quality code across the OpenManus frontend codebase while providing excellent developer experience through IDE integration and automated checks.
