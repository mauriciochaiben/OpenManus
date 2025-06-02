import React, { useState, useCallback } from 'react';
import {
    Card,
    Steps,
    Timeline,
    Typography,
    Space,
    Progress,
    Alert,
    Button,
    Tooltip,
    Tag,
    Spin
} from 'antd';
import {
    CheckCircleOutlined,
    CloseCircleOutlined,
    LoadingOutlined,
    ClockCircleOutlined,
    PlayCircleOutlined,
    ReloadOutlined,
    InfoCircleOutlined
} from '@ant-design/icons';
import { useWebSocket } from '../../../hooks/useWebSocket';

const { Step } = Steps;
const { Item: TimelineItem } = Timeline;
const { Text, Paragraph } = Typography;

interface WorkflowStep {
    id: string;
    name: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    result?: string;
    error?: string;
    startTime?: string;
    endTime?: string;
    duration?: number;
    agentRole?: string;
    contextEnhanced?: boolean;
}

interface WorkflowState {
    id: string;
    title: string;
    description?: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    steps: WorkflowStep[];
    startTime?: string;
    endTime?: string;
    totalDuration?: number;
    currentStepIndex?: number;
    contextEnhanced?: boolean;
}

interface WorkflowProgressProps {
    workflowId: string;
    showTimeline?: boolean;
    compact?: boolean;
    onWorkflowComplete?: (workflow: WorkflowState) => void;
    onWorkflowFailed?: (workflow: WorkflowState, error: string) => void;
}

const WorkflowProgress: React.FC<WorkflowProgressProps> = ({
    workflowId,
    showTimeline = false,
    compact = false,
    onWorkflowComplete,
    onWorkflowFailed
}) => {
    const [workflowState, setWorkflowState] = useState<WorkflowState | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // WebSocket connection for real-time updates
    const {
        isConnected,
        connectionState,
        connect: reconnect
    } = useWebSocket({
        autoConnect: true,
        onMessage: (message) => {
            try {
                // Filter events for this specific workflow
                if (message.workflow_id === workflowId) {
                    handleWorkflowEvent(message);
                }
            } catch (err) {
                console.error('Error handling WebSocket message:', err);
            }
        }
    });

    const connectionError = connectionState === 'disconnected';

    const handleWorkflowEvent = useCallback((event: any) => {
        const { type, ...eventData } = event;

        switch (type) {
            case 'workflow_started':
                setWorkflowState({
                    id: eventData.workflow_id,
                    title: eventData.title || 'Workflow',
                    description: eventData.description,
                    status: 'running',
                    steps: [],
                    startTime: eventData.timestamp || new Date().toISOString(),
                    contextEnhanced: eventData.context_enhanced
                });
                setLoading(false);
                break;

            case 'workflow_step_started':
                setWorkflowState(prev => {
                    if (!prev) return prev;

                    const updatedSteps = [...prev.steps];
                    const stepIndex = updatedSteps.findIndex(s => s.id === eventData.step_id);

                    if (stepIndex >= 0) {
                        updatedSteps[stepIndex] = {
                            ...updatedSteps[stepIndex],
                            status: 'running',
                            startTime: eventData.timestamp || new Date().toISOString(),
                            agentRole: eventData.agent_role
                        };
                    } else {
                        updatedSteps.push({
                            id: eventData.step_id,
                            name: eventData.step_name,
                            status: 'running',
                            startTime: eventData.timestamp || new Date().toISOString(),
                            agentRole: eventData.agent_role
                        });
                    }

                    return {
                        ...prev,
                        steps: updatedSteps,
                        currentStepIndex: stepIndex >= 0 ? stepIndex : updatedSteps.length - 1
                    };
                });
                break;

            case 'workflow_step_completed':
                setWorkflowState(prev => {
                    if (!prev) return prev;

                    const updatedSteps = [...prev.steps];
                    const stepIndex = updatedSteps.findIndex(s => s.id === eventData.step_id);

                    if (stepIndex >= 0) {
                        const endTime = eventData.timestamp || new Date().toISOString();
                        const startTime = updatedSteps[stepIndex].startTime;
                        const duration = startTime ?
                            (new Date(endTime).getTime() - new Date(startTime).getTime()) / 1000 : 0;

                        updatedSteps[stepIndex] = {
                            ...updatedSteps[stepIndex],
                            status: eventData.status === 'success' ? 'completed' : 'failed',
                            result: eventData.result,
                            error: eventData.error,
                            endTime,
                            duration,
                            contextEnhanced: eventData.context_enhanced
                        };
                    }

                    return {
                        ...prev,
                        steps: updatedSteps
                    };
                });
                break;

            case 'workflow_completed':
                setWorkflowState(prev => {
                    if (!prev) return prev;

                    const endTime = eventData.timestamp || new Date().toISOString();
                    const startTime = prev.startTime;
                    const totalDuration = startTime ?
                        (new Date(endTime).getTime() - new Date(startTime).getTime()) / 1000 : 0;

                    const completedWorkflow = {
                        ...prev,
                        status: 'completed' as const,
                        endTime,
                        totalDuration
                    };

                    onWorkflowComplete?.(completedWorkflow);
                    return completedWorkflow;
                });
                break;

            case 'workflow_failed':
                setWorkflowState(prev => {
                    if (!prev) return prev;

                    const endTime = eventData.timestamp || new Date().toISOString();
                    const startTime = prev.startTime;
                    const totalDuration = startTime ?
                        (new Date(endTime).getTime() - new Date(startTime).getTime()) / 1000 : 0;

                    const failedWorkflow = {
                        ...prev,
                        status: 'failed' as const,
                        endTime,
                        totalDuration
                    };

                    onWorkflowFailed?.(failedWorkflow, eventData.error);
                    return failedWorkflow;
                });
                setError(eventData.error);
                break;

            default:
                console.log('Unknown workflow event type:', type);
        }
    }, [onWorkflowComplete, onWorkflowFailed]);

    const getStepIcon = (step: WorkflowStep) => {
        switch (step.status) {
            case 'completed':
                return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
            case 'failed':
                return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
            case 'running':
                return <LoadingOutlined style={{ color: '#1890ff' }} />;
            case 'pending':
            default:
                return <ClockCircleOutlined style={{ color: '#d9d9d9' }} />;
        }
    };

    const getStepStatus = (step: WorkflowStep): 'wait' | 'process' | 'finish' | 'error' => {
        switch (step.status) {
            case 'completed':
                return 'finish';
            case 'failed':
                return 'error';
            case 'running':
                return 'process';
            case 'pending':
            default:
                return 'wait';
        }
    };

    const formatDuration = (seconds: number): string => {
        if (seconds < 60) {
            return `${seconds.toFixed(1)}s`;
        }
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}m ${remainingSeconds.toFixed(0)}s`;
    };

    const getWorkflowProgress = (): number => {
        if (!workflowState || workflowState.steps.length === 0) return 0;

        const completedSteps = workflowState.steps.filter(s =>
            s.status === 'completed' || s.status === 'failed'
        ).length;

        return (completedSteps / workflowState.steps.length) * 100;
    };

    const renderStepsView = () => {
        if (!workflowState) return null;

        return (
            <Steps
                current={workflowState.currentStepIndex}
                direction={compact ? 'horizontal' : 'vertical'}
                size={compact ? 'small' : 'default'}
            >
                {workflowState.steps.map((step) => (
                    <Step
                        key={step.id}
                        title={
                            <Space>
                                <span>{step.name}</span>
                                {step.agentRole && (
                                    <Tag color="blue">
                                        {step.agentRole}
                                    </Tag>
                                )}
                                {step.contextEnhanced && (
                                    <Tooltip title="Enhanced with knowledge context">
                                        <InfoCircleOutlined style={{ color: '#1890ff' }} />
                                    </Tooltip>
                                )}
                            </Space>
                        }
                        description={
                            <Space direction="vertical" size="small">
                                {step.result && (
                                    <Text type={step.status === 'failed' ? 'danger' : 'secondary'}>
                                        {step.result}
                                    </Text>
                                )}
                                {step.error && (
                                    <Text type="danger">{step.error}</Text>
                                )}
                                {step.duration && (
                                    <Text type="secondary" style={{ fontSize: '12px' }}>
                                        Duration: {formatDuration(step.duration)}
                                    </Text>
                                )}
                            </Space>
                        }
                        status={getStepStatus(step)}
                        icon={getStepIcon(step)}
                    />
                ))}
            </Steps>
        );
    };

    const renderTimelineView = () => {
        if (!workflowState) return null;

        return (
            <Timeline>
                <TimelineItem
                    color="blue"
                    dot={<PlayCircleOutlined />}
                >
                    <Space direction="vertical" size="small">
                        <Text strong>Workflow Started</Text>
                        <Text type="secondary">
                            {workflowState.startTime && new Date(workflowState.startTime).toLocaleString()}
                        </Text>
                    </Space>
                </TimelineItem>

                {workflowState.steps.map((step) => (
                    <TimelineItem
                        key={step.id}
                        color={
                            step.status === 'completed' ? 'green' :
                                step.status === 'failed' ? 'red' :
                                    step.status === 'running' ? 'blue' : 'gray'
                        }
                        dot={getStepIcon(step)}
                    >
                        <Space direction="vertical" size="small">
                            <Space>
                                <Text strong>{step.name}</Text>
                                {step.agentRole && (
                                    <Tag color="blue">
                                        {step.agentRole}
                                    </Tag>
                                )}
                            </Space>
                            {step.result && (
                                <Text type={step.status === 'failed' ? 'danger' : 'secondary'}>
                                    {step.result}
                                </Text>
                            )}
                            {step.startTime && (
                                <Text type="secondary" style={{ fontSize: '12px' }}>
                                    {new Date(step.startTime).toLocaleString()}
                                    {step.duration && ` • ${formatDuration(step.duration)}`}
                                </Text>
                            )}
                        </Space>
                    </TimelineItem>
                ))}

                {workflowState.status === 'completed' && (
                    <TimelineItem
                        color="green"
                        dot={<CheckCircleOutlined />}
                    >
                        <Space direction="vertical" size="small">
                            <Text strong>Workflow Completed</Text>
                            <Text type="secondary">
                                {workflowState.endTime && new Date(workflowState.endTime).toLocaleString()}
                                {workflowState.totalDuration &&
                                    ` • Total: ${formatDuration(workflowState.totalDuration)}`
                                }
                            </Text>
                        </Space>
                    </TimelineItem>
                )}

                {workflowState.status === 'failed' && (
                    <TimelineItem
                        color="red"
                        dot={<CloseCircleOutlined />}
                    >
                        <Space direction="vertical" size="small">
                            <Text strong>Workflow Failed</Text>
                            <Text type="secondary">
                                {workflowState.endTime && new Date(workflowState.endTime).toLocaleString()}
                            </Text>
                        </Space>
                    </TimelineItem>
                )}
            </Timeline>
        );
    };

    if (loading) {
        return (
            <Card>
                <div style={{ textAlign: 'center', padding: '40px' }}>
                    <Spin size="large" />
                    <div style={{ marginTop: '16px' }}>
                        <Text>Connecting to workflow...</Text>
                    </div>
                </div>
            </Card>
        );
    }

    if (connectionError) {
        return (
            <Card>
                <Alert
                    message="Connection Error"
                    description="Failed to connect to workflow updates"
                    type="error"
                    showIcon
                    action={
                        <Button size="small" onClick={reconnect} icon={<ReloadOutlined />}>
                            Retry
                        </Button>
                    }
                />
            </Card>
        );
    }

    if (!workflowState) {
        return (
            <Card>
                <Alert
                    message="Workflow Not Found"
                    description={`No workflow found with ID: ${workflowId}`}
                    type="warning"
                    showIcon
                />
            </Card>
        );
    }

    return (
        <Card
            title={
                <Space>
                    <span>{workflowState.title}</span>
                    {workflowState.contextEnhanced && (
                        <Tooltip title="This workflow uses knowledge context">
                            <Tag color="blue">Context Enhanced</Tag>
                        </Tooltip>
                    )}
                </Space>
            }
            extra={
                !isConnected && (
                    <Tooltip title="Disconnected from real-time updates">
                        <Button
                            size="small"
                            icon={<ReloadOutlined />}
                            onClick={reconnect}
                            type="text"
                        >
                            Reconnect
                        </Button>
                    </Tooltip>
                )
            }
        >
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
                {/* Workflow Description */}
                {workflowState.description && (
                    <Paragraph type="secondary">
                        {workflowState.description}
                    </Paragraph>
                )}

                {/* Progress Bar */}
                <div>
                    <div style={{ marginBottom: '8px' }}>
                        <Space>
                            <Text strong>Progress:</Text>
                            <Text>{Math.round(getWorkflowProgress())}%</Text>
                            {workflowState.totalDuration && (
                                <Text type="secondary">
                                    • {formatDuration(workflowState.totalDuration)}
                                </Text>
                            )}
                        </Space>
                    </div>
                    <Progress
                        percent={getWorkflowProgress()}
                        status={
                            workflowState.status === 'failed' ? 'exception' :
                                workflowState.status === 'completed' ? 'success' : 'active'
                        }
                        strokeColor={
                            workflowState.status === 'completed' ? '#52c41a' :
                                workflowState.status === 'failed' ? '#ff4d4f' : '#1890ff'
                        }
                    />
                </div>

                {/* Error Alert */}
                {error && (
                    <Alert
                        message="Workflow Failed"
                        description={error}
                        type="error"
                        showIcon
                        closable
                        onClose={() => setError(null)}
                    />
                )}

                {/* Steps or Timeline */}
                {showTimeline ? renderTimelineView() : renderStepsView()}
            </Space>
        </Card>
    );
};

export default WorkflowProgress;
