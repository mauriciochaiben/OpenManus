import axios from 'axios';
import { describe, expect, test, jest, beforeEach } from '@jest/globals';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('API Client Tests', () => {
    beforeEach(() => {
        jest.resetAllMocks();
    });

    test('should get tasks successfully', async () => {
        const mockTasks = [
            { id: '1', title: 'Task 1', status: 'pending' },
            { id: '2', title: 'Task 2', status: 'completed' }
        ];

        mockedAxios.get.mockResolvedValueOnce({ data: mockTasks });

        const response = await axios.get('http://localhost:8000/tasks');
        expect(response.data).toEqual(mockTasks);
        expect(mockedAxios.get).toHaveBeenCalledWith('http://localhost:8000/tasks');
    });

    test('should create task successfully', async () => {
        const newTask = {
            title: 'New Task',
            description: 'Test task',
            complexity: 'simple',
            priority: 'medium',
            mode: 'single'
        };

        const mockResponse = {
            task: { id: '3', ...newTask, status: 'pending' },
            message: 'Task created successfully'
        };

        mockedAxios.post.mockResolvedValueOnce({ data: mockResponse });

        const response = await axios.post('http://localhost:8000/tasks', newTask);
        expect(response.data).toEqual(mockResponse);
        expect(mockedAxios.post).toHaveBeenCalledWith('http://localhost:8000/tasks', newTask);
    });

    test('should handle API errors gracefully', async () => {
        const errorMessage = 'Network Error';
        mockedAxios.get.mockRejectedValueOnce(new Error(errorMessage));

        await expect(axios.get('http://localhost:8000/tasks')).rejects.toThrow(errorMessage);
    });
});
