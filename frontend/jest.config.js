/** @type {import('jest').Config} */
const config = {
  preset: 'ts-jest',
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['@testing-library/jest-dom'],

  // Define the working directory
  rootDir: '..',

  // Module resolution and mapping
  moduleNameMapper: {
    '\\.(css|less|scss|sass)$': 'identity-obj-proxy',
    '^@/(.*)$': '<rootDir>/frontend/src/$1',
    '^src/(.*)$': '<rootDir>/frontend/src/$1',
  },

  // TypeScript transformation
  transform: {
    '^.+\\.tsx?$': [
      'ts-jest',
      {
        tsconfig: '<rootDir>/frontend/tsconfig.json',
        useESM: false,
      },
    ],
  },

  // Test file patterns
  testMatch: ['<rootDir>/tests/frontend/**/*.{test,spec}.{ts,tsx}'],

  // Root directories for Jest to scan
  roots: ['<rootDir>/tests/frontend'],

  // Coverage configuration
  collectCoverageFrom: [
    'frontend/src/**/*.{ts,tsx}',
    '!frontend/src/**/*.d.ts',
    '!frontend/src/main.tsx',
    '!frontend/src/vite-env.d.ts',
  ],

  // Ignore patterns
  testPathIgnorePatterns: ['/node_modules/', '/dist/'],

  // Module file extensions
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],

  // Global variables
  globals: {
    'import.meta': {
      env: {
        VITE_API_BASE_URL: 'http://localhost:8000',
      },
    },
  },

  // Error handling
  errorOnDeprecated: false,
  clearMocks: true,
  restoreMocks: true,
};

module.exports = config;
