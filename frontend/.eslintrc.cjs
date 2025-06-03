module.exports = {
    root: true,
    env: {
        browser: true,
        es2020: true,
        node: true,
    },
    extends: [
        'eslint:recommended',
        'plugin:@typescript-eslint/recommended',
        'plugin:react/recommended',
        'plugin:react/jsx-runtime',
        'plugin:react-hooks/recommended',
        'prettier', // Must be last to override other formatting rules
    ],
    ignorePatterns: ['dist', '.eslintrc.cjs', 'vite.config.ts', 'vitest.config.ts'],
    parser: '@typescript-eslint/parser',
    parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        project: ['./tsconfig.json', './tsconfig.node.json'],
        tsconfigRootDir: __dirname,
        ecmaFeatures: {
            jsx: true,
        },
    },
    plugins: [
        'react',
        'react-hooks',
        'react-refresh',
        '@typescript-eslint',
        'prettier',
    ],
    settings: {
        react: {
            version: 'detect',
        },
    },
    rules: {
        // React rules
        'react/react-in-jsx-scope': 'off', // Not needed in React 17+
        'react/prop-types': 'off', // Using TypeScript for prop validation
        'react/jsx-uses-react': 'off', // Not needed in React 17+
        'react/jsx-uses-vars': 'error',
        'react/jsx-no-target-blank': 'error',
        'react/jsx-key': 'error',
        'react/no-array-index-key': 'warn',
        'react/no-unescaped-entities': 'warn',
        'react/display-name': 'warn',

        // React Hooks rules
        'react-hooks/rules-of-hooks': 'error',
        'react-hooks/exhaustive-deps': 'warn',

        // React Refresh
        'react-refresh/only-export-components': [
            'warn',
            { allowConstantExport: true },
        ],

        // TypeScript rules
        '@typescript-eslint/no-unused-vars': [
            'error',
            {
                argsIgnorePattern: '^_',
                varsIgnorePattern: '^_',
                ignoreRestSiblings: true,
            },
        ],
        '@typescript-eslint/explicit-function-return-type': 'off',
        '@typescript-eslint/explicit-module-boundary-types': 'off',
        '@typescript-eslint/no-explicit-any': 'warn',
        '@typescript-eslint/no-non-null-assertion': 'warn',
        '@typescript-eslint/no-var-requires': 'error',
        '@typescript-eslint/ban-ts-comment': 'warn',
        '@typescript-eslint/no-empty-function': 'warn',

        // General ESLint rules
        'no-console': 'warn',
        'no-debugger': 'error',
        'no-alert': 'warn',
        'no-var': 'error',
        'prefer-const': 'error',
        'no-unused-expressions': 'error',
        'no-duplicate-imports': 'error',
        'prefer-template': 'error',
        'yoda': 'error',

        // Code quality
        'complexity': ['warn', 10],
        'max-depth': ['warn', 4],
        'max-nested-callbacks': ['warn', 3],
        'max-params': ['warn', 4],

        // Prettier integration
        'prettier/prettier': 'error',
    },

    // File-specific overrides
    overrides: [
        {
            files: ['**/*.test.{ts,tsx}', '**/*.spec.{ts,tsx}'],
            env: {
                jest: true,
            },
            extends: ['plugin:testing-library/react'],
            rules: {
                '@typescript-eslint/no-explicit-any': 'off',
                'no-console': 'off',
            },
        },
        {
            files: ['vite.config.ts', '*.config.{js,ts}'],
            rules: {
                '@typescript-eslint/no-var-requires': 'off',
                'no-console': 'off',
            },
        },
        {
            files: ['src/types/**/*.ts'],
            rules: {
                '@typescript-eslint/no-explicit-any': 'off', // Type definitions may need any
            },
        },
    ],
};
