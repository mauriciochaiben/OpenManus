import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from '../../../frontend/src/App';

// Mock the WebSocket service
jest.mock('../../../frontend/src/services/websocket', () => {
    const mockWebSocketService = {
        subscribe: jest.fn(),
        unsubscribe: jest.fn(),
        connect: jest.fn(),
        disconnect: jest.fn(),
        subscribeToSystem: jest.fn(),
        unsubscribeFromTask: jest.fn(),
        subscribeToTask: jest.fn(),
        on: jest.fn(),
        off: jest.fn(),
        emit: jest.fn(),
        isSocketConnected: jest.fn(() => false),
        reconnect: jest.fn(),
        destroy: jest.fn(),
    };

    return {
        __esModule: true,
        default: mockWebSocketService,
        WebSocketService: jest.fn().mockImplementation(() => mockWebSocketService),
    };
});

// Mock the API service
jest.mock('../../../frontend/src/services/api', () => ({
    getTasks: jest.fn(() => Promise.resolve([])),
    createTask: jest.fn(),
    getTask: jest.fn(),
    updateTask: jest.fn(),
    deleteTask: jest.fn(),
    getSystemHealth: jest.fn(() => Promise.resolve({ status: 'healthy' })),
}));

// Don't mock react-router-dom - let it work normally for App tests

describe('App Component', () => {
    let queryClient: QueryClient;

    beforeEach(() => {
        queryClient = new QueryClient({
            defaultOptions: {
                queries: {
                    retry: false,
                },
            },
        });
    });

    afterEach(() => {
        queryClient.clear();
    });

    it('renders without crashing', () => {
        render(
            <QueryClientProvider client={queryClient}>
                <App />
            </QueryClientProvider>
        );

        expect(screen.getByText('OpenManus')).toBeInTheDocument();
    });

    it('renders sidebar navigation', () => {
        render(
            <QueryClientProvider client={queryClient}>
                <App />
            </QueryClientProvider>
        );

        expect(screen.getByText('Home')).toBeInTheDocument();
        expect(screen.getByText('MCP Config')).toBeInTheDocument();
        expect(screen.getByText('Settings')).toBeInTheDocument();
    });

    it('renders header with correct title', () => {
        render(
            <QueryClientProvider client={queryClient}>
                <App />
            </QueryClientProvider>
        );

        expect(screen.getByText('AI Assistant Dashboard')).toBeInTheDocument();
    });
});
