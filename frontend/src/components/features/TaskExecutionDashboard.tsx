import React, { useEffect, useState } from 'react';
import {
  Card,
  Progress,
  Timeline,
  Typography,
  Space,
  Tag,
  Alert,
  Spin,
} from 'antd';
import {
  PlayCircleOutlined,
  PauseCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined,
  RobotOutlined,
} from '@ant-design/icons';
import { useTask } from '../../hooks/useTasks';
import { eventBus } from '../../utils/eventBus';
import type { ExecutionStep, TaskExecution } from '../../types';

const { Title, Text, Paragraph } = Typography;

interface TaskExecutionDashboardProps {
  taskId: string;
}

const TaskExecutionDashboard: React.FC<TaskExecutionDashboardProps> = ({
  taskId,
}) => {
  const { task, loading, error } = useTask(taskId);
  const [execution, setExecution] = useState<TaskExecution | null>(null);
  const [steps, setSteps] = useState<ExecutionStep[]>([]);

  useEffect(() => {
    // Subscribe to task updates using EventBus
    const unsubscribeTask = eventBus.on('task:updated', (data: any) => {
      if (data.task_id === taskId) {
        // Task data will be automatically updated through React Query
      }
    });

    // Subscribe to execution updates
    const unsubscribeExecution = eventBus.on(
      'task:executionUpdated',
      (data: any) => {
        if (data.task_id === taskId) {
          setExecution(data.execution);
        }
      }
    );

    // Subscribe to step updates
    const unsubscribeStep = eventBus.on('task:stepUpdated', (data: any) => {
      if (data.task_id === taskId) {
        setSteps((prev) => {
          const existingIndex = prev.findIndex(
            (step) => step.id === data.step.id
          );
          if (existingIndex >= 0) {
            const newSteps = [...prev];
            newSteps[existingIndex] = data.step;
            return newSteps;
          } else {
            return [...prev, data.step].sort(
              (a, b) => a.step_number - b.step_number
            );
          }
        });
      }
    });

    return () => {
      unsubscribeTask();
      unsubscribeExecution();
      unsubscribeStep();
    };
  }, [taskId]);

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '40px' }}>
        <Spin size='large' />
        <p style={{ marginTop: '16px' }}>Loading task execution...</p>
      </div>
    );
  }

  if (error || !task) {
    return (
      <Alert
        message='Error'
        description='Failed to load task execution data'
        type='error'
        showIcon
      />
    );
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <PlayCircleOutlined style={{ color: '#1890ff' }} />;
      case 'paused':
        return <PauseCircleOutlined style={{ color: '#faad14' }} />;
      case 'completed':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'failed':
        return <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return <ClockCircleOutlined style={{ color: '#d9d9d9' }} />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'processing';
      case 'paused':
        return 'warning';
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const calculateProgress = () => {
    if (!execution || steps.length === 0) return 0;
    const completedSteps = steps.filter(
      (step) => step.status === 'completed'
    ).length;
    return Math.round((completedSteps / steps.length) * 100);
  };

  return (
    <div style={{ padding: '24px' }}>
      <Space direction='vertical' style={{ width: '100%' }} size='large'>
        {/* Task Header */}
        <Card>
          <Space direction='vertical' style={{ width: '100%' }}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
              }}
            >
              <div style={{ flex: 1 }}>
                <Title level={3} style={{ margin: 0 }}>
                  {task.title}
                </Title>
                <Paragraph style={{ marginTop: '8px', marginBottom: '16px' }}>
                  {task.description}
                </Paragraph>
                <Space>
                  <Tag color={getStatusColor(task.status)}>
                    {getStatusIcon(task.status)} {task.status.toUpperCase()}
                  </Tag>
                  <Tag color='blue'>{task.complexity.toUpperCase()}</Tag>
                  {/* <Tag color="purple">{task.priority?.toUpperCase()}</Tag> */}
                </Space>
              </div>
            </div>
          </Space>
        </Card>

        {/* Execution Progress */}
        {execution && (
          <Card title='Execution Progress'>
            <Space direction='vertical' style={{ width: '100%' }}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                }}
              >
                <Text strong>Overall Progress</Text>
                <Text>{calculateProgress()}%</Text>
              </div>
              <Progress
                percent={calculateProgress()}
                status={task.status === 'error' ? 'exception' : 'active'}
                strokeColor={{
                  '0%': '#108ee9',
                  '100%': '#87d068',
                }}
              />

              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  marginTop: '16px',
                }}
              >
                <div>
                  <Text type='secondary'>Started: </Text>
                  <Text>{new Date(execution.started_at).toLocaleString()}</Text>
                </div>
                {execution.completed_at && (
                  <div>
                    <Text type='secondary'>Completed: </Text>
                    <Text>
                      {new Date(execution.completed_at).toLocaleString()}
                    </Text>
                  </div>
                )}
              </div>
            </Space>
          </Card>
        )}

        {/* Execution Steps */}
        {steps.length > 0 && (
          <Card title='Execution Steps'>
            <Timeline>
              {steps.map((step) => (
                <Timeline.Item
                  key={step.id}
                  dot={getStatusIcon(step.status)}
                  color={
                    step.status === 'completed'
                      ? 'green'
                      : step.status === 'failed'
                        ? 'red'
                        : step.status === 'running'
                          ? 'blue'
                          : 'gray'
                  }
                >
                  <Space direction='vertical' style={{ width: '100%' }}>
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                      }}
                    >
                      <Text strong>
                        Step {step.step_number}: {step.title}
                      </Text>
                      <Tag color={getStatusColor(step.status)}>
                        {step.status.toUpperCase()}
                      </Tag>
                    </div>

                    {step.description && (
                      <Text type='secondary'>{step.description}</Text>
                    )}

                    {step.agent_name && (
                      <div>
                        <RobotOutlined style={{ marginRight: '8px' }} />
                        <Text>Executed by: {step.agent_name}</Text>
                      </div>
                    )}

                    {step.started_at && (
                      <div>
                        <Text type='secondary' style={{ fontSize: '12px' }}>
                          Started: {new Date(step.started_at).toLocaleString()}
                          {step.completed_at && (
                            <>
                              {' '}
                              • Completed:{' '}
                              {new Date(step.completed_at).toLocaleString()}
                            </>
                          )}
                        </Text>
                      </div>
                    )}

                    {step.error_message && (
                      <Alert
                        message='Error'
                        description={step.error_message}
                        type='error'
                        showIcon
                      />
                    )}

                    {step.output && step.output.trim() && (
                      <Card
                        size='small'
                        style={{ background: '#f5f5f5', marginTop: '8px' }}
                      >
                        <Text
                          code
                          style={{ whiteSpace: 'pre-wrap', fontSize: '12px' }}
                        >
                          {step.output}
                        </Text>
                      </Card>
                    )}
                  </Space>
                </Timeline.Item>
              ))}
            </Timeline>
          </Card>
        )}

        {/* Task Documents - Temporarily commented to fix TypeScript errors */}
        {/* {task.documents && task.documents.length > 0 && (
                    <Card title="Associated Documents">
                        <Space direction="vertical" style={{ width: '100%' }}>
                            {task.documents.map((doc: any) => (
                                <div
                                    key={doc.id}
                                    style={{
                                        padding: '12px',
                                        border: '1px solid #f0f0f0',
                                        borderRadius: '6px',
                                        background: '#fafafa'
                                    }}
                                >
                                    <Text strong>{doc.name}</Text>
                                    <br />
                                    <Text type="secondary">
                                        {doc.type} • {(doc.size / 1024 / 1024).toFixed(2)} MB
                                    </Text>
                                </div>
                            ))}
                        </Space>
                    </Card>
                )} */}
      </Space>
    </div>
  );
};

export default TaskExecutionDashboard;
