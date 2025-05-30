import React, { useState } from 'react';
import { Card, List, Typography, Space, Button, Tag, Empty, Spin, message } from 'antd';
import { PlusOutlined, EyeOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useTasks } from '../hooks/useTasks';
import TaskCreationForm from '../components/features/TaskCreationForm';
import type { Task } from '../types';

const { Title, Text } = Typography;

const HomePage: React.FC = () => {
    const navigate = useNavigate();
    const { data: tasks, isLoading, error } = useTasks();
    const [showCreateForm, setShowCreateForm] = useState(false);

    const handleTaskCreated = (taskId: string) => {
        setShowCreateForm(false);
        message.success('Task created successfully!');
        navigate(`/task/${taskId}`);
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'running': return 'processing';
            case 'paused': return 'warning';
            case 'completed': return 'success';
            case 'failed': return 'error';
            default: return 'default';
        }
    };

    const formatTimeAgo = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));

        if (diffInHours < 1) return 'Just now';
        if (diffInHours < 24) return `${diffInHours}h ago`;
        return `${Math.floor(diffInHours / 24)}d ago`;
    };

    if (showCreateForm) {
        return <TaskCreationForm onTaskCreated={handleTaskCreated} />;
    }

    return (
        <div style={{ padding: '24px', marginLeft: '250px' }}>
            <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
                <Space direction="vertical" style={{ width: '100%' }} size="large">
                    {/* Header */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <Title level={2} style={{ margin: 0 }}>
                                Welcome to OpenManus
                            </Title>
                            <Text type="secondary">
                                Create and manage your AI-powered tasks
                            </Text>
                        </div>
                        <Button
                            type="primary"
                            size="large"
                            icon={<PlusOutlined />}
                            onClick={() => setShowCreateForm(true)}
                        >
                            Create Task
                        </Button>
                    </div>

                    {/* Quick Stats */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                        <Card>
                            <div style={{ textAlign: 'center' }}>
                                <Title level={3} style={{ color: '#1890ff', margin: '0 0 8px 0' }}>
                                    {tasks?.filter(t => t.status === 'running').length || 0}
                                </Title>
                                <Text type="secondary">Running Tasks</Text>
                            </div>
                        </Card>
                        <Card>
                            <div style={{ textAlign: 'center' }}>
                                <Title level={3} style={{ color: '#52c41a', margin: '0 0 8px 0' }}>
                                    {tasks?.filter(t => t.status === 'completed').length || 0}
                                </Title>
                                <Text type="secondary">Completed Tasks</Text>
                            </div>
                        </Card>
                        <Card>
                            <div style={{ textAlign: 'center' }}>
                                <Title level={3} style={{ color: '#faad14', margin: '0 0 8px 0' }}>
                                    {tasks?.filter(t => t.status === 'pending').length || 0}
                                </Title>
                                <Text type="secondary">Pending Tasks</Text>
                            </div>
                        </Card>
                        <Card>
                            <div style={{ textAlign: 'center' }}>
                                <Title level={3} style={{ color: '#722ed1', margin: '0 0 8px 0' }}>
                                    {tasks?.length || 0}
                                </Title>
                                <Text type="secondary">Total Tasks</Text>
                            </div>
                        </Card>
                    </div>

                    {/* Recent Tasks */}
                    <Card title="Recent Tasks">
                        {isLoading ? (
                            <div style={{ textAlign: 'center', padding: '40px' }}>
                                <Spin size="large" />
                            </div>
                        ) : error ? (
                            <Empty description="Failed to load tasks" />
                        ) : !tasks || tasks.length === 0 ? (
                            <Empty
                                description="No tasks yet"
                                image={Empty.PRESENTED_IMAGE_SIMPLE}
                            >
                                <Button
                                    type="primary"
                                    icon={<PlusOutlined />}
                                    onClick={() => setShowCreateForm(true)}
                                >
                                    Create Your First Task
                                </Button>
                            </Empty>
                        ) : (
                            <List
                                dataSource={tasks.slice(0, 10)} // Show only recent 10 tasks
                                renderItem={(task: Task) => (
                                    <List.Item
                                        actions={[
                                            <Button
                                                type="link"
                                                icon={<EyeOutlined />}
                                                onClick={() => navigate(`/task/${task.id}`)}
                                            >
                                                View Details
                                            </Button>
                                        ]}
                                    >
                                        <List.Item.Meta
                                            title={
                                                <Space>
                                                    <span>{task.title}</span>
                                                    <Tag color={getStatusColor(task.status)}>
                                                        {task.status.toUpperCase()}
                                                    </Tag>
                                                </Space>
                                            }
                                            description={
                                                <Space direction="vertical" size="small">
                                                    <Text type="secondary">{task.description}</Text>
                                                    <Space>
                                                        <Tag color="blue">{task.complexity}</Tag>
                                                        <Tag color="purple">{task.priority}</Tag>
                                                        {task.tags?.map(tag => (
                                                            <Tag key={tag}>{tag}</Tag>
                                                        ))}
                                                    </Space>
                                                    <Space>
                                                        <ClockCircleOutlined />
                                                        <Text type="secondary">
                                                            Created {formatTimeAgo(task.created_at)}
                                                        </Text>
                                                    </Space>
                                                </Space>
                                            }
                                        />
                                    </List.Item>
                                )}
                            />
                        )}
                    </Card>
                </Space>
            </div>
        </div>
    );
};

export default HomePage;
