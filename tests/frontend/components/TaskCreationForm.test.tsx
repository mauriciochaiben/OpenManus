import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import TaskCreationForm from '../../../frontend/src/components/features/TaskCreationForm';
import * as api from '../../../frontend/src/services/api';

// Mock the API
jest.mock('../../../frontend/src/services/api');
const mockCreateTask = jest.mocked(api.createTask);

// Mock DocumentUpload component
jest.mock('../../../frontend/src/components/features/DocumentUpload', () => {
    return function MockDocumentUpload({ onUploadSuccess }: any) {
        return (
            <div data-testid="document-upload">
                <button
                    onClick={() => onUploadSuccess([
                        { id: '1', name: 'test.pdf', size: 1024, type: 'pdf' }
                    ])}
                >
                    Mock Upload
                </button>
            </div>
        );
    };
});

const mockOnTaskCreated = jest.fn();

describe('TaskCreationForm Component', () => {
    beforeEach(() => {
        mockCreateTask.mockClear();
        mockOnTaskCreated.mockClear();
    });

    it('renders form elements correctly', () => {
        render(<TaskCreationForm onTaskCreated={mockOnTaskCreated} />);

        expect(screen.getByText('Create New Task')).toBeInTheDocument();
        expect(screen.getByLabelText(/task title/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/task description/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/complexity level/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/priority/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /create task/i })).toBeInTheDocument();
    });

    it('shows validation errors for required fields', async () => {
        const user = userEvent.setup();
        render(<TaskCreationForm onTaskCreated={mockOnTaskCreated} />);

        const createButton = screen.getByRole('button', { name: /create task/i });
        await user.click(createButton);

        await waitFor(() => {
            expect(screen.getByText('Please enter a task title')).toBeInTheDocument();
            expect(screen.getByText('Please enter a task description')).toBeInTheDocument();
            expect(screen.getByText('Please select a complexity level')).toBeInTheDocument();
        });
    });

    it('submits form with correct data', async () => {
        const user = userEvent.setup();
        const mockTaskResponse = {
            task: {
                id: 'task-123',
                title: 'Test Task',
                description: 'Test task description',
                complexity: 'complex' as const,
                status: 'pending' as const,
                mode: 'auto' as const,
                createdAt: new Date().toISOString()
            },
            message: 'Task created successfully'
        };
        mockCreateTask.mockResolvedValue(mockTaskResponse);

        render(<TaskCreationForm onTaskCreated={mockOnTaskCreated} />);

        // Fill form fields
        await user.type(screen.getByLabelText(/task title/i), 'Test Task Title');
        await user.type(screen.getByLabelText(/task description/i), 'Test task description');

        // Select complexity
        await user.click(screen.getByLabelText(/complexity level/i));
        await user.click(screen.getByText('Medium - Moderate complexity, may require multiple steps'));

        // Select priority
        await user.click(screen.getByLabelText(/priority/i));
        await user.click(screen.getByText('High'));

        // Add tags
        await user.type(screen.getByLabelText(/tags/i), 'test, automation, demo');

        // Submit form
        await user.click(screen.getByRole('button', { name: /create task/i }));

        await waitFor(() => {
            expect(mockCreateTask).toHaveBeenCalledWith({
                title: 'Test Task Title',
                description: 'Test task description',
                complexity: 'medium',
                priority: 'high',
                document_ids: [],
                tags: ['test', 'automation', 'demo'],
            });
        });

        expect(mockOnTaskCreated).toHaveBeenCalledWith('task-123');
    });

    it('handles document upload correctly', async () => {
        const user = userEvent.setup();
        const mockTaskResponse = {
            task: {
                id: 'task-456',
                title: 'Task with Documents',
                description: 'Task with uploaded documents',
                complexity: 'simple' as const,
                status: 'pending' as const,
                mode: 'auto' as const,
                createdAt: new Date().toISOString()
            },
            message: 'Task created successfully'
        };
        mockCreateTask.mockResolvedValue(mockTaskResponse);

        render(<TaskCreationForm onTaskCreated={mockOnTaskCreated} />);

        // Upload document
        await user.click(screen.getByText('Mock Upload'));

        // Wait for document to appear
        await waitFor(() => {
            expect(screen.getByText('test.pdf')).toBeInTheDocument();
        });

        // Fill required fields
        await user.type(screen.getByLabelText(/task title/i), 'Task with Documents');
        await user.type(screen.getByLabelText(/task description/i), 'Task with uploaded documents');

        await user.click(screen.getByLabelText(/complexity level/i));
        await user.click(screen.getByText('Low - Simple tasks, quick execution'));

        // Submit form
        await user.click(screen.getByRole('button', { name: /create task/i }));

        await waitFor(() => {
            expect(mockCreateTask).toHaveBeenCalledWith(
                expect.objectContaining({
                    document_ids: ['1'],
                })
            );
        });
    });

    it('removes uploaded documents correctly', async () => {
        const user = userEvent.setup();
        render(<TaskCreationForm onTaskCreated={mockOnTaskCreated} />);

        // Upload document
        await user.click(screen.getByText('Mock Upload'));

        // Wait for document to appear
        await waitFor(() => {
            expect(screen.getByText('test.pdf')).toBeInTheDocument();
        });

        // Remove document
        await user.click(screen.getByText('Remove'));

        // Document should be removed
        await waitFor(() => {
            expect(screen.queryByText('test.pdf')).not.toBeInTheDocument();
        });
    });

    it('handles API errors gracefully', async () => {
        const user = userEvent.setup();
        const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => { });
        mockCreateTask.mockRejectedValue(new Error('API Error'));

        render(<TaskCreationForm onTaskCreated={mockOnTaskCreated} />);

        // Fill required fields
        await user.type(screen.getByLabelText(/task title/i), 'Test Task');
        await user.type(screen.getByLabelText(/task description/i), 'Test description');

        await user.click(screen.getByLabelText(/complexity level/i));
        await user.click(screen.getByText('Low - Simple tasks, quick execution'));

        // Submit form
        await user.click(screen.getByRole('button', { name: /create task/i }));

        await waitFor(() => {
            expect(consoleSpy).toHaveBeenCalledWith('Failed to create task:', expect.any(Error));
        });

        expect(mockOnTaskCreated).not.toHaveBeenCalled();
        consoleSpy.mockRestore();
    });

    it('resets form after successful submission', async () => {
        const user = userEvent.setup();
        const mockTaskResponse = {
            task: {
                id: 'task-789',
                title: 'Reset Test',
                description: 'Test description',
                complexity: 'simple' as const,
                status: 'pending' as const,
                mode: 'auto' as const,
                createdAt: new Date().toISOString()
            },
            message: 'Task created successfully'
        };
        mockCreateTask.mockResolvedValue(mockTaskResponse);

        render(<TaskCreationForm onTaskCreated={mockOnTaskCreated} />);

        // Fill form
        await user.type(screen.getByLabelText(/task title/i), 'Test Task');
        await user.type(screen.getByLabelText(/task description/i), 'Test description');
        await user.click(screen.getByLabelText(/complexity level/i));
        await user.click(screen.getByText('Low - Simple tasks, quick execution'));

        // Submit form
        await user.click(screen.getByRole('button', { name: /create task/i }));

        // Wait for form submission to complete
        await waitFor(() => {
            expect(mockOnTaskCreated).toHaveBeenCalledWith('task-789');
        });

        // Wait for form reset - verify form fields are empty by checking they have placeholder text only
        await waitFor(() => {
            const titleInput = screen.getByLabelText(/task title/i) as HTMLInputElement;
            const descriptionInput = screen.getByLabelText(/task description/i) as HTMLTextAreaElement;

            expect(titleInput).toHaveValue('');
            expect(descriptionInput).toHaveValue('');
        });
    });
});
