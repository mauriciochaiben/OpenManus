module.exports = {
    // Core formatting options
    semi: true,
    trailingComma: 'es5',
    singleQuote: true,
    printWidth: 100, // Increased for modern development
    tabWidth: 2,
    useTabs: false,
    endOfLine: 'lf',

    // JavaScript/TypeScript specific
    quoteProps: 'as-needed',
    jsxSingleQuote: true,
    bracketSpacing: true,
    bracketSameLine: false,
    arrowParens: 'always',

    // HTML/JSX
    htmlWhitespaceSensitivity: 'css',
    jsxBracketSameLine: false,

    // File specific overrides
    overrides: [
        {
            files: '*.json',
            options: {
                printWidth: 120,
                tabWidth: 2,
            },
        },
        {
            files: '*.md',
            options: {
                proseWrap: 'always',
                printWidth: 80,
                tabWidth: 2,
            },
        },
        {
            files: ['*.yml', '*.yaml'],
            options: {
                tabWidth: 2,
                singleQuote: false,
            },
        },
        {
            files: '*.css',
            options: {
                singleQuote: false,
            },
        },
        {
            files: ['*.ts', '*.tsx'],
            options: {
                parser: 'typescript',
            },
        },
    ],
};
