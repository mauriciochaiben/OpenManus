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
        <div style={{ marginLeft: '250px', minHeight: '100vh', background: '#f5f5f5' }}>
            <div style={{ padding: '24px' }}>
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
