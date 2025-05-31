import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import TaskExecutionDashboard from '../../components/features/TaskExecutionDashboard';
import { useTask } from '../../hooks/useTasks';
import { eventBus } from '../../utils/eventBus';

// Mock the hooks and utilities
vi.mock('../../hooks/useTasks');
vi.mock('../../utils/eventBus');

const mockUseTask = useTask as any;
const mockEventBus = eventBus as any;

const mockTask = {
    id: 'task-1',
    title: 'Test Task',
    description: 'Test task description',
    complexity: 'medium' as const,
    mode: 'auto' as const,
    status: 'running' as const,
    progress: 45,
    createdAt: '2024-01-01T00:00:00Z',
    updatedAt: '2024-01-01T01:00:00Z',
    priority: 'high' as const,
    tags: ['test', 'automation'],
    documentIds: ['doc-1'],
    steps: [
        {
            id: 'step-1',
            stepNumber: 1,
            title: 'Initialize Task',
            description: 'Setting up the task environment',
            status: 'completed' as const,
            startedAt: '2024-01-01T00:00:00Z',
            completedAt: '2024-01-01T00:05:00Z',
            agentName: 'Setup Agent',
            output: 'Task environment initialized successfully',
        }
    ],
};

describe('TaskExecutionDashboard Component', () => {
    beforeEach(() => {
        vi.clearAllMocks();

        // Setup default mock return values
        mockEventBus.on = vi.fn().mockReturnValue(vi.fn());
        mockEventBus.off = vi.fn();
        mockEventBus.emit = vi.fn();
    });

    afterEach(() => {
        vi.clearAllMocks();
    });

    it('renders loading state', () => {
        mockUseTask.mockReturnValue({
            task: null,
            loading: true,
            error: null,
        });

        render(<TaskExecutionDashboard taskId="task-1" />);

        expect(screen.getByText('Loading task execution...')).toBeInTheDocument();
    });

    it('renders error state', () => {
        const errorMessage = 'Failed to load task execution data';
        mockUseTask.mockReturnValue({
            task: null,
            loading: false,
            error: errorMessage,
        });

        render(<TaskExecutionDashboard taskId="task-1" />);

        expect(screen.getByText(errorMessage)).toBeInTheDocument();
    });

    it('renders task data when available', () => {
        mockUseTask.mockReturnValue({
            task: mockTask,
            loading: false,
            error: null,
        });

        render(<TaskExecutionDashboard taskId="task-1" />);

        expect(screen.getByText('Test Task')).toBeInTheDocument();
        expect(screen.getByText('Test task description')).toBeInTheDocument();
    });

    it('registers event listeners', () => {
        mockUseTask.mockReturnValue({
            task: mockTask,
            loading: false,
            error: null,
        });

        render(<TaskExecutionDashboard taskId="task-1" />);

        // Check that component registers event listeners
        expect(mockEventBus.on).toHaveBeenCalledWith('task:executionUpdated', expect.any(Function));
        expect(mockEventBus.on).toHaveBeenCalledWith('task:stepUpdated', expect.any(Function));
    });

    it('component handles task prop changes', () => {
        mockUseTask.mockReturnValue({
            task: mockTask,
            loading: false,
            error: null,
        });

        const { rerender } = render(<TaskExecutionDashboard taskId="task-1" />);
        
        // Rerender with different taskId
        rerender(<TaskExecutionDashboard taskId="task-2" />);

        // Should re-fetch task data when taskId changes
        expect(mockUseTask).toHaveBeenCalledWith('task-2');
    });
});