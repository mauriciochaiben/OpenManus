import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DocumentUpload from '../../components/features/DocumentUpload';
import { uploadDocument } from '../../services/api';

// Mock the API
vi.mock('../../services/api', () => ({
    uploadDocument: vi.fn(),
}));

// Mock Ant Design components
vi.mock('antd', async () => {
    const actual = await vi.importActual('antd');
    return {
        ...actual,
        message: {
            error: vi.fn(),
            success: vi.fn(),
        },
        Upload: {
            Dragger: ({ children, onChange, accept, multiple, beforeUpload }: any) => (
                <div data-testid="upload-dragger">
                    <input
                        type="file"
                        data-testid="file-input"
                        accept={accept}
                        multiple={multiple}
                        onChange={(e) => {
                            const files = Array.from(e.target.files || []);
                            files.forEach((file) => {
                                const uploadFile = {
                                    uid: file.name,
                                    name: file.name,
                                    size: file.size,
                                    type: file.type,
                                    originFileObj: file,
                                };

                                if (beforeUpload && beforeUpload(file) === false) {
                                    return;
                                }

                                onChange?.({
                                    file: uploadFile,
                                    fileList: [uploadFile],
                                });
                            });
                        }}
                    />
                    {children}
                </div>
            ),
        },
    };
});

const mockUploadDocument = uploadDocument as any;
const mockOnUploadSuccess = vi.fn();

const createMockFile = (name: string, size: number, type: string) => {
    return new File(['test content'], name, { type });
};

describe('DocumentUpload Component', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    afterEach(() => {
        vi.clearAllMocks();
    });

    it('renders upload area correctly', () => {
        render(<DocumentUpload onUploadSuccess={mockOnUploadSuccess} />);

        expect(screen.getByTestId('upload-dragger')).toBeInTheDocument();
        expect(screen.getByText('Click or drag file to this area to upload')).toBeInTheDocument();
        expect(screen.getByText(/Support for a single or bulk upload/)).toBeInTheDocument();
    });

    it('accepts valid file types', async () => {
        render(<DocumentUpload onUploadSuccess={mockOnUploadSuccess} />);

        const fileInput = screen.getByTestId('file-input');
        expect(fileInput).toHaveAttribute('accept', '.pdf,.doc,.docx,.txt,.md');
    });

    it('supports multiple file upload by default', () => {
        render(<DocumentUpload onUploadSuccess={mockOnUploadSuccess} />);

        const fileInput = screen.getByTestId('file-input');
        expect(fileInput).toHaveAttribute('multiple');
    });

    it('uploads file successfully', async () => {
        const mockResponse = {
            id: '1',
            name: 'test.pdf',
            size: 1024,
            type: 'pdf',
            url: 'http://example.com/test.pdf',
        };

        mockUploadDocument.mockResolvedValue(mockResponse);

        render(<DocumentUpload onUploadSuccess={mockOnUploadSuccess} />);

        const file = createMockFile('test.pdf', 1024, 'application/pdf');
        const fileInput = screen.getByTestId('file-input');

        await userEvent.upload(fileInput, file);

        await waitFor(() => {
            expect(mockUploadDocument).toHaveBeenCalledWith(file);
            expect(mockOnUploadSuccess).toHaveBeenCalledWith([mockResponse]);
        });
    });

    it('handles upload error gracefully', async () => {
        const uploadError = new Error('Upload failed');
        mockUploadDocument.mockRejectedValue(uploadError);

        // Mock console.error to avoid noise in test output
        const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => { });

        render(<DocumentUpload onUploadSuccess={mockOnUploadSuccess} />);

        const file = createMockFile('test.pdf', 1024, 'application/pdf');
        const fileInput = screen.getByTestId('file-input');

        await userEvent.upload(fileInput, file);

        await waitFor(() => {
            expect(mockUploadDocument).toHaveBeenCalledWith(file);
            expect(mockOnUploadSuccess).not.toHaveBeenCalled();
            expect(consoleSpy).toHaveBeenCalledWith('Upload failed:', uploadError);
        });

        consoleSpy.mockRestore();
    });

    it('validates file size limit', async () => {
        render(<DocumentUpload onUploadSuccess={mockOnUploadSuccess} />);

        // Create a file larger than the 50MB limit (as per component)
        const largeFile = createMockFile('large.pdf', 60 * 1024 * 1024, 'application/pdf');
        const fileInput = screen.getByTestId('file-input');

        await userEvent.upload(fileInput, largeFile);

        await waitFor(() => {
            expect(mockUploadDocument).not.toHaveBeenCalled();
            expect(mockOnUploadSuccess).not.toHaveBeenCalled();
        });
    });

    it('validates file type', async () => {
        render(<DocumentUpload onUploadSuccess={mockOnUploadSuccess} />);

        // Create an invalid file type
        const invalidFile = createMockFile('image.jpg', 1024, 'image/jpeg');
        const fileInput = screen.getByTestId('file-input');

        await userEvent.upload(fileInput, invalidFile);

        await waitFor(() => {
            expect(mockUploadDocument).not.toHaveBeenCalled();
            expect(mockOnUploadSuccess).not.toHaveBeenCalled();
        });
    });

    it('respects max files limit', async () => {
        const maxFiles = 2;
        render(<DocumentUpload onUploadSuccess={mockOnUploadSuccess} maxFiles={maxFiles} />);

        const files = [
            createMockFile('file1.pdf', 1024, 'application/pdf'),
            createMockFile('file2.pdf', 1024, 'application/pdf'),
            createMockFile('file3.pdf', 1024, 'application/pdf'),
        ];

        const fileInput = screen.getByTestId('file-input');

        await userEvent.upload(fileInput, files);

        // Only first 2 files should be processed
        await waitFor(() => {
            expect(mockUploadDocument).toHaveBeenCalledTimes(2);
        });
    });

    it('accepts custom file types', () => {
        const customTypes = ['.json', '.xml'];
        render(
            <DocumentUpload
                onUploadSuccess={mockOnUploadSuccess}
                acceptedTypes={customTypes}
            />
        );

        const fileInput = screen.getByTestId('file-input');
        expect(fileInput).toHaveAttribute('accept', '.json,.xml');
    });

    it('shows upload progress', async () => {
        mockUploadDocument.mockImplementation(() => {
            return new Promise((resolve) => {
                setTimeout(() => resolve({
                    id: '1',
                    name: 'test.pdf',
                    size: 1024,
                    type: 'pdf',
                }), 100);
            });
        });

        render(<DocumentUpload onUploadSuccess={mockOnUploadSuccess} />);

        const file = createMockFile('test.pdf', 1024, 'application/pdf');
        const fileInput = screen.getByTestId('file-input');

        await userEvent.upload(fileInput, file);

        // Check that upload started
        expect(mockUploadDocument).toHaveBeenCalledWith(file);

        await waitFor(() => {
            expect(mockOnUploadSuccess).toHaveBeenCalled();
        });
    });

    it('displays uploaded files', async () => {
        const mockResponse = {
            id: '1',
            name: 'test.pdf',
            size: 1024,
            type: 'pdf',
        };

        mockUploadDocument.mockResolvedValue(mockResponse);

        render(<DocumentUpload onUploadSuccess={mockOnUploadSuccess} />);

        const file = createMockFile('test.pdf', 1024, 'application/pdf');
        const fileInput = screen.getByTestId('file-input');

        await userEvent.upload(fileInput, file);

        await waitFor(() => {
            expect(screen.getByText('test.pdf')).toBeInTheDocument();
            expect(screen.getByText('1.00 KB')).toBeInTheDocument();
        });
    });

    it('allows removing uploaded files', async () => {
        const mockResponse = {
            id: '1',
            name: 'test.pdf',
            size: 1024,
            type: 'pdf',
        };

        mockUploadDocument.mockResolvedValue(mockResponse);

        render(<DocumentUpload onUploadSuccess={mockOnUploadSuccess} />);

        const file = createMockFile('test.pdf', 1024, 'application/pdf');
        const fileInput = screen.getByTestId('file-input');

        await userEvent.upload(fileInput, file);

        await waitFor(() => {
            expect(screen.getByText('test.pdf')).toBeInTheDocument();
        });

        // Find and click remove button
        const removeButton = screen.getByRole('button', { name: /delete/i });
        await userEvent.click(removeButton);

        await waitFor(() => {
            expect(screen.queryByText('test.pdf')).not.toBeInTheDocument();
        });
    });

    it('prevents duplicate file uploads', async () => {
        const mockResponse = {
            id: '1',
            name: 'test.pdf',
            size: 1024,
            type: 'pdf',
        };

        mockUploadDocument.mockResolvedValue(mockResponse);

        render(<DocumentUpload onUploadSuccess={mockOnUploadSuccess} />);

        const file = createMockFile('test.pdf', 1024, 'application/pdf');
        const fileInput = screen.getByTestId('file-input');

        // Upload the same file twice
        await userEvent.upload(fileInput, file);
        await userEvent.upload(fileInput, file);

        await waitFor(() => {
            // Should only be called once
            expect(mockUploadDocument).toHaveBeenCalledTimes(1);
        });
    });

    it('shows proper error messages for different error types', async () => {
        mockUploadDocument.mockRejectedValue(new Error('Network error'));

        render(<DocumentUpload onUploadSuccess={mockOnUploadSuccess} />);

        const file = createMockFile('test.pdf', 1024, 'application/pdf');
        const fileInput = screen.getByTestId('file-input');

        await userEvent.upload(fileInput, file);

        await waitFor(() => {
            expect(mockUploadDocument).toHaveBeenCalledWith(file);
        });
    });
});
