import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import HomePage from '../../../frontend/src/pages/HomePage';
import * as tasksHook from '../../../frontend/src/hooks/useTasks';

// Mock the hooks
jest.mock('../../../frontend/src/hooks/useTasks');
const mockUseTasks = jest.mocked(tasksHook.useTasks);

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
    ...jest.requireActual('react-router-dom'),
    useNavigate: () => mockNavigate,
}));

// Mock WebSocket service
jest.mock('../../../frontend/src/services/websocket', () => ({
    WebSocketService: {
        getInstance: jest.fn(() => ({
            subscribe: jest.fn(),
            unsubscribe: jest.fn(),
        })),
    },
}));

const mockTasks = [
    {
        id: '1',
        title: 'Test Task 1',
        description: 'This is a test task',
        status: 'running',
        complexity: 'complex',
        mode: 'auto',
        createdAt: '2024-01-01T00:00:00Z',
    },
    {
        id: '2',
        title: 'Test Task 2',
        description: 'Another test task',
        status: 'completed',
        complexity: 'simple',
        mode: 'single',
        createdAt: '2024-01-02T00:00:00Z',
    },
];

const renderHomePage = () => {
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: { retry: false },
        },
    });

    return render(
        <QueryClientProvider client={queryClient}>
            <BrowserRouter>
                <HomePage />
            </BrowserRouter>
        </QueryClientProvider>
    );
};

describe('HomePage Component', () => {
    beforeEach(() => {
        mockNavigate.mockClear();
    });

    it('renders welcome message and create task button', () => {
        mockUseTasks.mockReturnValue({
            data: mockTasks,
            isLoading: false,
            error: null,
        } as any);

        renderHomePage();

        expect(screen.getByText('Welcome to OpenManus')).toBeInTheDocument();
        expect(screen.getByText('Create and manage your AI-powered tasks')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /create task/i })).toBeInTheDocument();
    });

    it('displays task statistics correctly', () => {
        mockUseTasks.mockReturnValue({
            tasks: mockTasks,
            loading: false,
            error: null,
        } as any);

        renderHomePage();

        // Check for Running Tasks (should be 1)
        expect(screen.getByText('Running Tasks')).toBeInTheDocument();
        // Check for Completed Tasks (should be 1)
        expect(screen.getByText('Completed Tasks')).toBeInTheDocument();
        // Check for Total Tasks (should be 2)
        expect(screen.getByText('Total Tasks')).toBeInTheDocument();

        // Verify the task titles are displayed
        expect(screen.getByText('Test Task 1')).toBeInTheDocument();
        expect(screen.getByText('Test Task 2')).toBeInTheDocument();
    });

    it('displays task list with correct information', () => {
        mockUseTasks.mockReturnValue({
            tasks: mockTasks,
            loading: false,
            error: null,
        } as any);

        renderHomePage();

        expect(screen.getByText('Test Task 1')).toBeInTheDocument();
        expect(screen.getByText('Test Task 2')).toBeInTheDocument();
        expect(screen.getByText('RUNNING')).toBeInTheDocument();
        expect(screen.getByText('COMPLETED')).toBeInTheDocument();
    });

    it('shows loading state when tasks are loading', () => {
        mockUseTasks.mockReturnValue({
            tasks: [],
            loading: true,
            error: null,
        } as any);

        renderHomePage();

        expect(screen.getByTestId('loading')).toBeInTheDocument();
    });

    it('shows empty state when no tasks exist', () => {
        mockUseTasks.mockReturnValue({
            tasks: [],
            loading: false,
            error: null,
        } as any);

        renderHomePage();

        expect(screen.getByText('No tasks yet')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /create your first task/i })).toBeInTheDocument();
    });

    it('navigates to task detail page when view details is clicked', async () => {
        mockUseTasks.mockReturnValue({
            tasks: mockTasks,
            loading: false,
            error: null,
        } as any);

        renderHomePage();

        const viewDetailsButtons = screen.getAllByText('View Details');
        fireEvent.click(viewDetailsButtons[0]);

        await waitFor(() => {
            expect(mockNavigate).toHaveBeenCalledWith('/task/1');
        });
    });

    it('shows create task form when create task button is clicked', async () => {
        mockUseTasks.mockReturnValue({
            data: mockTasks,
            isLoading: false,
            error: null,
        } as any);

        renderHomePage();

        const createTaskButton = screen.getByRole('button', { name: /create task/i });
        fireEvent.click(createTaskButton);

        await waitFor(() => {
            expect(screen.getByText('Create New Task')).toBeInTheDocument();
        });
    });
});
