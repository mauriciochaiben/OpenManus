import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider, theme, Layout, Typography, Input, Button, Card, Space, Alert, Spin, Upload, message } from 'antd';
import { PlayCircleOutlined, ClearOutlined, UploadOutlined, FileTextOutlined } from '@ant-design/icons';
import { NotificationProvider } from './contexts/NotificationContext';
import MainChatInterface from './components/chat/MainChatInterface';
import StatusBar from './components/layout/StatusBar';
import Knowledge from './pages/Knowledge';
import './App.css';

const { Header, Content } = Layout;
const { Title, Text } = Typography;
const { TextArea } = Input;
const { Dragger } = Upload;

interface WorkflowStatus {
    id?: string;
    status: 'idle' | 'running' | 'completed' | 'failed';
    currentStep?: string;
    results: Array<{
        step: string;
        status: string;
        result?: string;
        timestamp: string;
    }>;
    error?: string;
}

interface WorkflowEvent {
    type: 'workflow_started' | 'workflow_step_started' | 'workflow_step_completed' | 'workflow_completed' | 'workflow_failed';
    workflow_id: string;
    step_name?: string;
    status?: string;
    result?: string;
    error?: string;
    timestamp: string;
}

// Custom hook for WebSocket workflow events
const useWorkflowWebSocket = (onMessage: (event: WorkflowEvent) => void) => {
    const [ws, setWs] = useState<WebSocket | null>(null);
    const [isConnected, setIsConnected] = useState(false);

    useEffect(() => {
        const websocket = new WebSocket('ws://localhost:8000/ws/workflow');

        websocket.onopen = () => {
            setIsConnected(true);
            console.log('WebSocket connected');
        };

        websocket.onmessage = (event) => {
            try {
                const data: WorkflowEvent = JSON.parse(event.data);
                onMessage(data);
            } catch (error) {
                console.error('Failed to parse WebSocket message:', error);
            }
        };

        websocket.onclose = () => {
            setIsConnected(false);
            console.log('WebSocket disconnected');
        };

        websocket.onerror = (error) => {
            console.error('WebSocket error:', error);
        };

        setWs(websocket);

        return () => {
            websocket.close();
        };
    }, [onMessage]);

    return { ws, isConnected };
};

interface DocumentUploadStatus {
    uploading: boolean;
    uploaded: string[];
    failed: string[];
}

const App: React.FC = () => {
    const [taskInput, setTaskInput] = useState<string>('');
    const [workflowStatus, setWorkflowStatus] = useState<WorkflowStatus>({
        status: 'idle',
        results: []
    });
    const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
    const [documentUpload, setDocumentUpload] = useState<DocumentUploadStatus>({
        uploading: false,
        uploaded: [],
        failed: []
    });

    // Handle WebSocket workflow events
    const handleWorkflowEvent = useCallback((event: WorkflowEvent) => {
        console.log('Received workflow event:', event);

        setWorkflowStatus(prev => {
            switch (event.type) {
                case 'workflow_started':
                    return {
                        ...prev,
                        id: event.workflow_id,
                        status: 'running',
                        currentStep: 'Workflow started...',
                        results: [],
                        error: undefined
                    };

                case 'workflow_step_started':
                    return {
                        ...prev,
                        currentStep: `Executing step: ${event.step_name}`
                    };

                case 'workflow_step_completed':
                    const newResult = {
                        step: event.step_name || 'Unknown step',
                        status: event.status || 'completed',
                        result: event.result,
                        timestamp: event.timestamp
                    };
                    return {
                        ...prev,
                        results: [...prev.results, newResult],
                        currentStep: `Step ${event.step_name} completed`
                    };

                case 'workflow_completed':
                    return {
                        ...prev,
                        status: 'completed',
                        currentStep: undefined
                    };

                case 'workflow_failed':
                    return {
                        ...prev,
                        status: 'failed',
                        currentStep: undefined,
                        error: event.error || 'Workflow failed'
                    };

                default:
                    return prev;
            }
        });
    }, []);

    // Initialize WebSocket connection
    const { isConnected } = useWorkflowWebSocket(handleWorkflowEvent);

    const handleSubmit = async () => {
        if (!taskInput.trim()) return;

        setIsSubmitting(true);
        setWorkflowStatus({
            status: 'running',
            results: [],
            currentStep: 'Initializing workflow...'
        });

        try {
            const response = await fetch('http://localhost:8000/workflows/simple', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    title: 'User Task',
                    description: taskInput,
                    steps: [
                        {
                            name: 'plan_task',
                            agent_type: 'planner',
                            config: { objective: taskInput }
                        },
                        {
                            name: 'execute_plan',
                            agent_type: 'tool_user',
                            config: { tools: ['file_manager', 'code_editor'] }
                        }
                    ]
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Workflow started:', data);

            // The WebSocket will handle real-time updates
            setIsSubmitting(false);

        } catch (error) {
            console.error('Failed to start workflow:', error);
            setWorkflowStatus({
                status: 'failed',
                results: [],
                error: error instanceof Error ? error.message : 'Failed to start workflow'
            });
            setIsSubmitting(false);
        }
    };

    const handleClear = () => {
        setTaskInput('');
        setWorkflowStatus({
            status: 'idle',
            results: []
        });
    };

    const handleFileUpload = async (file: File) => {
        setDocumentUpload(prev => ({ ...prev, uploading: true }));

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:8000/knowledge/sources/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.status}`);
            }

            const data = await response.json();

            setDocumentUpload(prev => ({
                ...prev,
                uploading: false,
                uploaded: [...prev.uploaded, data.source_id]
            }));

            message.success(`Document "${file.name}" uploaded successfully!`);

        } catch (error) {
            console.error('Upload failed:', error);
            setDocumentUpload(prev => ({
                ...prev,
                uploading: false,
                failed: [...prev.failed, file.name]
            }));

            message.error(`Failed to upload "${file.name}"`);
        }
    };

    const uploadProps = {
        name: 'file',
        multiple: false,
        accept: '.pdf,.txt,.md,.docx,.html,.json,.csv',
        beforeUpload: (file: File) => {
            handleFileUpload(file);
            return false; // Prevent automatic upload
        },
        onDrop(e: React.DragEvent<HTMLDivElement>) {
            console.log('Dropped files', e.dataTransfer.files);
        },
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'running': return 'processing';
            case 'completed': return 'success';
            case 'failed': return 'error';
            default: return 'default';
        }
    };

    return (
        <ConfigProvider
            theme={{
                algorithm: theme.defaultAlgorithm,
                token: {
                    colorPrimary: '#6366f1',
                    borderRadius: 8,
                    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
                    colorBgContainer: '#ffffff',
                    colorBgLayout: '#f5f5f5',
                },
            }}
        >
            <NotificationProvider>
                <Router>
                    <div className="app-container">
                        <StatusBar />
                        <Layout className="app-layout">
                            <Header className="app-header">
                                <div className="header-content">
                                    <Title level={2} className="header-title">
                                        OpenManus - AI Workflow Assistant
                                    </Title>
                                    <div className="connection-status">
                                        <Text className="connection-text">
                                            WebSocket: {isConnected ? '🟢 Connected' : '🔴 Disconnected'}
                                        </Text>
                                    </div>
                                </div>
                            </Header>

                            <Content className="app-content">
                                <div className="content-wrapper">
                                    <Space direction="vertical" size={24} className="main-space">
                                        {/* Document Upload Section */}
                                        <Card
                                            title={
                                                <Space>
                                                    <FileTextOutlined />
                                                    <span>Upload Documents</span>
                                                </Space>
                                            }
                                            className="upload-card"
                                            bordered
                                        >
                                            <Dragger {...uploadProps} className="upload-dragger">
                                                <p className="ant-upload-drag-icon">
                                                    <UploadOutlined />
                                                </p>
                                                <p className="ant-upload-text">
                                                    Click or drag files to upload
                                                </p>
                                                <p className="ant-upload-hint">
                                                    Support for PDF, TXT, MD, DOCX, HTML, JSON, CSV files
                                                </p>
                                            </Dragger>

                                            {(documentUpload.uploaded.length > 0 || documentUpload.failed.length > 0) && (
                                                <div style={{ marginTop: 16 }}>
                                                    {documentUpload.uploaded.length > 0 && (
                                                        <Alert
                                                            message={`${documentUpload.uploaded.length} document(s) uploaded successfully`}
                                                            type="success"
                                                            showIcon
                                                            style={{ marginBottom: 8 }}
                                                        />
                                                    )}
                                                    {documentUpload.failed.length > 0 && (
                                                        <Alert
                                                            message={`${documentUpload.failed.length} upload(s) failed`}
                                                            type="error"
                                                            showIcon
                                                        />
                                                    )}
                                                </div>
                                            )}
                                        </Card>

                                        {/* Task Input Section */}
                                        <Card
                                            title="Describe Your Task"
                                            className="task-input-card"
                                            bordered
                                        >
                                            <div className="task-input-content">
                                                <TextArea
                                                    value={taskInput}
                                                    onChange={(e) => setTaskInput(e.target.value)}
                                                    placeholder="Describe what you want to accomplish... (e.g., 'Create a Python script to analyze CSV data and generate a report')"
                                                    rows={4}
                                                    disabled={workflowStatus.status === 'running'}
                                                    className="task-textarea"
                                                    showCount
                                                    maxLength={1000}
                                                />

                                                <div className="task-actions">
                                                    <Space size="middle">
                                                        <Button
                                                            type="primary"
                                                            icon={<PlayCircleOutlined />}
                                                            onClick={handleSubmit}
                                                            loading={isSubmitting}
                                                            disabled={!taskInput.trim() || workflowStatus.status === 'running' || !isConnected}
                                                            size="large"
                                                            className="start-button"
                                                        >
                                                            Start Workflow
                                                        </Button>

                                                        <Button
                                                            icon={<ClearOutlined />}
                                                            onClick={handleClear}
                                                            disabled={workflowStatus.status === 'running'}
                                                            size="large"
                                                            className="clear-button"
                                                        >
                                                            Clear
                                                        </Button>
                                                    </Space>
                                                </div>

                                                {!isConnected && (
                                                    <Alert
                                                        message="WebSocket Disconnected"
                                                        description="Real-time updates are not available. Please refresh the page to reconnect."
                                                        type="warning"
                                                        showIcon
                                                        className="connection-alert"
                                                    />
                                                )}
                                            </div>
                                        </Card>

                                        {/* Workflow Status Section */}
                                        {workflowStatus.status !== 'idle' && (
                                            <Card
                                                title="Workflow Status"
                                                className="workflow-status-card"
                                                bordered
                                                extra={
                                                    <div className="status-badge">
                                                        <Text type="secondary" className="status-label">
                                                            Status:
                                                        </Text>
                                                        <Text
                                                            strong
                                                            className={`status-value status-${workflowStatus.status}`}
                                                        >
                                                            {workflowStatus.status.charAt(0).toUpperCase() + workflowStatus.status.slice(1)}
                                                        </Text>
                                                    </div>
                                                }
                                            >
                                                <div className="workflow-content">
                                                    {/* Current Step */}
                                                    {workflowStatus.currentStep && (
                                                        <Alert
                                                            message="Current Step"
                                                            description={
                                                                <div className="current-step">
                                                                    <Spin size="small" />
                                                                    <Text className="step-text">{workflowStatus.currentStep}</Text>
                                                                </div>
                                                            }
                                                            type="info"
                                                            showIcon
                                                            className="step-alert"
                                                        />
                                                    )}

                                                    {/* Error Display */}
                                                    {workflowStatus.error && (
                                                        <Alert
                                                            message="Workflow Failed"
                                                            description={workflowStatus.error}
                                                            type="error"
                                                            showIcon
                                                            className="error-alert"
                                                        />
                                                    )}

                                                    {/* Results Display */}
                                                    {workflowStatus.results.length > 0 && (
                                                        <div className="results-section">
                                                            <Title level={4} className="results-title">
                                                                Execution Results
                                                            </Title>
                                                            <div className="results-list">
                                                                {workflowStatus.results.map((result, index) => (
                                                                    <Card
                                                                        key={index}
                                                                        size="small"
                                                                        className="result-card"
                                                                        title={
                                                                            <div className="result-header">
                                                                                <Text strong className="step-name">
                                                                                    {result.step}
                                                                                </Text>
                                                                                <Text
                                                                                    className={`step-status step-status-${result.status}`}
                                                                                >
                                                                                    [{result.status}]
                                                                                </Text>
                                                                            </div>
                                                                        }
                                                                        extra={
                                                                            <Text type="secondary" className="timestamp">
                                                                                {new Date(result.timestamp).toLocaleTimeString()}
                                                                            </Text>
                                                                        }
                                                                    >
                                                                        {result.result && (
                                                                            <div className="result-content">
                                                                                <Text code className="result-text">
                                                                                    {result.result}
                                                                                </Text>
                                                                            </div>
                                                                        )}
                                                                    </Card>
                                                                ))}
                                                            </div>
                                                        </div>
                                                    )}

                                                    {/* Success Message */}
                                                    {workflowStatus.status === 'completed' && (
                                                        <Alert
                                                            message="Workflow Completed Successfully"
                                                            description="All steps have been executed successfully. Check the results above for details."
                                                            type="success"
                                                            showIcon
                                                            className="success-alert"
                                                        />
                                                    )}
                                                </div>
                                            </Card>
                                        )}
                                    </Space>
                                </div>
                            </Content>
                        </Layout>
                    </div>
                </Router>
            </NotificationProvider>
        </ConfigProvider>
    );
};

export default App;
