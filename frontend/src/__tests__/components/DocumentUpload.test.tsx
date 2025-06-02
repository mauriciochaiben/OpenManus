import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import DocumentUpload from '../../components/features/DocumentUpload';

// Mock the API
vi.mock('../../services/api', () => ({
    uploadDocument: vi.fn(),
}));

// Mock Ant Design message
vi.mock('antd', async () => {
    const actual = await vi.importActual('antd');
    return {
        ...actual,
        message: {
            error: vi.fn(),
            success: vi.fn(),
            warning: vi.fn(),
        },
    };
});

const mockOnUploadSuccess = vi.fn();

describe('DocumentUpload Component', () => {
    beforeEach(() => {
        vi.clearAllMocks();
    });

    afterEach(() => {
        vi.clearAllMocks();
    });

    it('renders upload area correctly', () => {
        render(<DocumentUpload onUploadSuccess={mockOnUploadSuccess} />);

        expect(screen.getByText('Document Upload')).toBeInTheDocument();
        expect(screen.getByText('Click or drag files to this area to upload')).toBeInTheDocument();
        expect(screen.getByText(/Support for.*files\. Maximum file size: 50MB/)).toBeInTheDocument();
    });

    it('renders with default props', () => {
        render(<DocumentUpload onUploadSuccess={mockOnUploadSuccess} />);

        expect(screen.getByText(/You can upload up to 10 files at once/)).toBeInTheDocument();
        expect(screen.getByText(/\.pdf, \.doc, \.docx, \.txt, \.md/)).toBeInTheDocument();
    });

    it('renders with custom props', () => {
        render(
            <DocumentUpload
                onUploadSuccess={mockOnUploadSuccess}
                maxFiles={5}
                acceptedTypes={['.json', '.xml']}
            />
        );

        expect(screen.getByText(/You can upload up to 5 files at once/)).toBeInTheDocument();
        expect(screen.getByText(/\.json, \.xml/)).toBeInTheDocument();
    });

    it('handles onUploadSuccess prop', () => {
        const onUploadSuccess = vi.fn();
        render(<DocumentUpload onUploadSuccess={onUploadSuccess} />);

        // Component should render without errors
        expect(screen.getByText('Document Upload')).toBeInTheDocument();
    });

    it('renders without onUploadSuccess prop', () => {
        render(<DocumentUpload />);

        // Component should render without errors
        expect(screen.getByText('Document Upload')).toBeInTheDocument();
    });
});
