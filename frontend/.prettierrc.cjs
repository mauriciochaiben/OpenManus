module.exports = {
    // Formatting options
    semi: true,
    trailingComma: 'es5',
    singleQuote: true,
    printWidth: 80,
    tabWidth: 2,
    useTabs: false,

    // JavaScript/TypeScript
    quoteProps: 'as-needed',
    jsxSingleQuote: true,
    bracketSpacing: true,
    bracketSameLine: false,
    arrowParens: 'always',

    // File specific overrides
    overrides: [
        {
            files: '*.json',
            options: {
                printWidth: 200,
            },
        },
        {
            files: '*.md',
            options: {
                proseWrap: 'always',
                printWidth: 80,
            },
        },
    ],
};
