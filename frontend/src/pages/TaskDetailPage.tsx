import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button, Space } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import TaskExecutionDashboard from '../components/features/TaskExecutionDashboard';

const TaskDetailPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();

    if (!id) {
        return <div>Task ID not found</div>;
    }

    return (
        <div style={{ minHeight: '100vh', background: '#f5f5f5' }}>
            <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
                <Space style={{ marginBottom: '24px' }}>
                    <Button
                        icon={<ArrowLeftOutlined />}
                        onClick={() => navigate('/')}
                    >
                        Back to Home
                    </Button>
                </Space>

                <TaskExecutionDashboard taskId={id} />
            </div>
        </div>
    );
};

export default TaskDetailPage;
