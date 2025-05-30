// Export Jest configuration for frontend tests
const { defaults } = require('jest-config');

module.exports = {
    rootDir: '../../frontend',
    preset: 'ts-jest',
    testEnvironment: 'jest-environment-jsdom',
    setupFilesAfterEnv: ['jest-extended', '@testing-library/jest-dom'],
    moduleNameMapper: {
        '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
        '^src/(.*)$': '<rootDir>/src/$1',
    },
    transform: {
        '^.+\\.tsx?$': ['ts-jest', {
            tsconfig: '<rootDir>/tsconfig.json',
        }],
    },
    testMatch: [
        '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
        '<rootDir>/src/**/*.{spec,test}.{js,jsx,ts,tsx}',
        '../../tests/frontend/**/*.{spec,test}.{js,jsx,ts,tsx}',
    ],
    moduleFileExtensions: [...defaults.moduleFileExtensions, 'ts', 'tsx'],
    verbose: true
};
