# Shared Components and Utils Migration

## Overview

This document tracks the reorganization of shared components, hooks, and
utilities from feature-specific directories to centralized shared directories.

## Migrated Components

### SourceSelector

- **Original Location**:
  `frontend/src/features/knowledge/components/SourceSelector.tsx`
- **New Location**: `frontend/src/shared/components/SourceSelector.tsx`
- **Used By**:
  - Knowledge feature (maintains backward compatibility)
  - Notes feature (updated import)
- **Dependencies**: Still imports `useKnowledgeSources` from knowledge feature
- **Status**: ✅ Migrated and imports updated

## Migrated Utils

### Clipboard Utilities

- **New Location**: `frontend/src/shared/utils/clipboard.ts`
- **Functions**:
  - `copyToClipboard(text: string)` - Copy text with fallback for older browsers
  - `isClipboardAvailable()` - Check if clipboard API is available
- **Migrated From**: `frontend/src/features/chat/utils/messageActions.ts`
- **Status**: ✅ Created and chat feature updated to use shared version

### Text and Data Formatters

- **New Location**: `frontend/src/shared/utils/formatters.ts`
- **Functions**:
  - `capitalize(str: string)` - Capitalize first letter
  - `truncateText(text: string, maxLength: number)` - Truncate with ellipsis
  - `formatFileSize(bytes: number)` - Human readable file sizes
  - `formatRelativeTime(date: Date)` - Relative time format
  - `formatJSON(obj: any, indent: number)` - Pretty print JSON
  - `stripMarkdown(text: string)` - Remove markdown formatting
- **Status**: ✅ Created - ready for use

### Validation Utilities

- **New Location**: `frontend/src/shared/utils/validation.ts`
- **Functions**:
  - `isValidEmail(email: string)` - Email validation
  - `isValidUrl(url: string)` - URL validation
  - `isEmpty(value: any)` - Check for empty values
  - `validateRequired(obj: object, fields: string[])` - Required field
    validation
  - `isAlphanumeric(str: string, allowedChars: string)` - Character validation
  - `validatePassword(password: string)` - Password strength validation
  - `sanitizeHtml(html: string)` - XSS prevention
  - `isValidJson(str: string)` - JSON validation
- **Status**: ✅ Created - ready for use

## Directory Structure

```
frontend/src/shared/
├── components/
│   ├── index.ts           # Exports all shared components
│   └── SourceSelector.tsx # Knowledge source selection component
├── hooks/                 # Empty - ready for shared hooks
├── types/                 # Existing shared types
└── utils/
    ├── index.ts          # Exports all utility functions
    ├── clipboard.ts      # Clipboard operations
    ├── formatters.ts     # Text and data formatting
    └── validation.ts     # Data validation utilities
```

## Import Patterns

### Shared Utils

```typescript
// Import specific utilities
import { copyToClipboard, isValidEmail } from '../../../shared/utils';

// Import from specific modules
import { formatFileSize, truncateText } from '../../../shared/utils/formatters';
import { validatePassword } from '../../../shared/utils/validation';
```

### Shared Components

```typescript
// Import shared components
import { SourceSelector } from '../../../shared/components';
```

## Migration Benefits

1. **Code Reusability**: Common utilities are now centralized and can be used
   across all features
2. **Consistency**: Shared components ensure consistent UI/UX across features
3. **Maintainability**: Single source of truth for common functionality
4. **Performance**: Reduced bundle size through better code sharing
5. **Type Safety**: Centralized utilities with proper TypeScript types

## Backward Compatibility

- All existing imports continue to work through re-exports
- Features maintain their own exports for components they originally owned
- No breaking changes for existing code

## Next Steps

1. **Move Additional Utilities**: Identify more utilities that can be shared
2. **Create Shared Hooks**: Move commonly used hooks to `shared/hooks/`
3. **Performance Optimization**: Implement tree-shaking optimizations
4. **Documentation**: Add JSDoc comments to all shared utilities
5. **Testing**: Add unit tests for shared utilities

## Usage Guidelines

1. **Naming**: Use descriptive names for utility functions
2. **Documentation**: Include JSDoc comments with examples
3. **Type Safety**: Ensure all functions have proper TypeScript types
4. **Error Handling**: Include proper error handling in utilities
5. **Backward Compatibility**: Maintain re-exports for moved components

## Status Summary

- ✅ Shared utils structure created
- ✅ Clipboard utilities migrated
- ✅ Text formatters created
- ✅ Validation utilities created
- ✅ SourceSelector component migrated
- ✅ Import paths updated
- ✅ Backward compatibility maintained
