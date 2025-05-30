import React, { useState } from 'react';
import { Form, Input, Select, Button, Card, Space, Typography, Divider, Alert } from 'antd';
import { PlusOutlined, RocketOutlined } from '@ant-design/icons';
import { createTask } from '../../services/api';
import type { TaskCreateRequest, DocumentUploadResponse } from '../../types';
import DocumentUpload from './DocumentUpload';

const { TextArea } = Input;
const { Option } = Select;
const { Title, Text } = Typography;

interface TaskCreationFormProps {
    onTaskCreated?: (taskId: string) => void;
}

const TaskCreationForm: React.FC<TaskCreationFormProps> = ({ onTaskCreated }) => {
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);
    const [uploadedDocuments, setUploadedDocuments] = useState<DocumentUploadResponse[]>([]);

    const complexityOptions = [
        { value: 'low', label: 'Low - Simple tasks, quick execution' },
        { value: 'medium', label: 'Medium - Moderate complexity, may require multiple steps' },
        { value: 'high', label: 'High - Complex tasks, multi-agent coordination' },
    ];

    const handleUploadSuccess = (files: DocumentUploadResponse[]) => {
        setUploadedDocuments(prev => [...prev, ...files]);
    };

    const handleSubmit = async (values: any) => {
        setLoading(true);

        try {
            const taskData: TaskCreateRequest = {
                title: values.title,
                description: values.description,
                complexity: values.complexity,
                document_ids: uploadedDocuments.map(doc => doc.id),
                priority: values.priority || 'medium',
                tags: values.tags ? values.tags.split(',').map((tag: string) => tag.trim()) : [],
            };

            const response = await createTask(taskData);

            if (onTaskCreated) {
                onTaskCreated(response.id);
            }

            // Reset form
            form.resetFields();
            setUploadedDocuments([]);

        } catch (error) {
            console.error('Failed to create task:', error);
        } finally {
            setLoading(false);
        }
    };

    const removeDocument = (docId: string) => {
        setUploadedDocuments(prev => prev.filter(doc => doc.id !== docId));
    };

    return (
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
            <Card className="task-creation-card">
                <Space direction="vertical" style={{ width: '100%' }} size="large">
                    <div style={{ textAlign: 'center' }}>
                        <RocketOutlined style={{ fontSize: '48px', color: '#1890ff', marginBottom: '16px' }} />
                        <Title level={2}>Create New Task</Title>
                        <Text type="secondary">
                            Define your task and upload any relevant documents to get started
                        </Text>
                    </div>

                    <Divider />

                    <Form
                        form={form}
                        layout="vertical"
                        onFinish={handleSubmit}
                        requiredMark={false}
                    >
                        <Form.Item
                            label="Task Title"
                            name="title"
                            rules={[{ required: true, message: 'Please enter a task title' }]}
                        >
                            <Input
                                placeholder="Enter a clear, descriptive title for your task"
                                size="large"
                            />
                        </Form.Item>

                        <Form.Item
                            label="Task Description"
                            name="description"
                            rules={[{ required: true, message: 'Please enter a task description' }]}
                        >
                            <TextArea
                                placeholder="Describe what you want to accomplish in detail. Be specific about your requirements and expected outcomes."
                                rows={4}
                                size="large"
                            />
                        </Form.Item>

                        <Form.Item
                            label="Complexity Level"
                            name="complexity"
                            rules={[{ required: true, message: 'Please select a complexity level' }]}
                        >
                            <Select placeholder="Select the expected complexity of your task" size="large">
                                {complexityOptions.map(option => (
                                    <Option key={option.value} value={option.value}>
                                        {option.label}
                                    </Option>
                                ))}
                            </Select>
                        </Form.Item>

                        <Form.Item
                            label="Priority"
                            name="priority"
                            initialValue="medium"
                        >
                            <Select size="large">
                                <Option value="low">Low</Option>
                                <Option value="medium">Medium</Option>
                                <Option value="high">High</Option>
                                <Option value="urgent">Urgent</Option>
                            </Select>
                        </Form.Item>

                        <Form.Item
                            label="Tags (optional)"
                            name="tags"
                        >
                            <Input
                                placeholder="Enter tags separated by commas (e.g., analysis, research, automation)"
                                size="large"
                            />
                        </Form.Item>
                    </Form>

                    <Divider />

                    <DocumentUpload
                        onUploadSuccess={handleUploadSuccess}
                        maxFiles={5}
                    />

                    {uploadedDocuments.length > 0 && (
                        <Card title="Uploaded Documents" size="small">
                            <Space direction="vertical" style={{ width: '100%' }}>
                                {uploadedDocuments.map(doc => (
                                    <div
                                        key={doc.id}
                                        style={{
                                            display: 'flex',
                                            justifyContent: 'space-between',
                                            alignItems: 'center',
                                            padding: '8px 12px',
                                            background: '#f5f5f5',
                                            borderRadius: '6px'
                                        }}
                                    >
                                        <div>
                                            <Text strong>{doc.filename}</Text>
                                            <br />
                                            <Text type="secondary" style={{ fontSize: '12px' }}>
                                                {doc.file_type} • {(doc.file_size / 1024 / 1024).toFixed(2)} MB
                                            </Text>
                                        </div>
                                        <Button
                                            type="text"
                                            danger
                                            onClick={() => removeDocument(doc.id)}
                                            size="small"
                                        >
                                            Remove
                                        </Button>
                                    </div>
                                ))}
                            </Space>
                        </Card>
                    )}

                    <Alert
                        message="Task Execution"
                        description="Once created, your task will be analyzed and executed by our AI assistant system. You'll be able to track progress in real-time and receive notifications about important updates."
                        type="info"
                        showIcon
                    />

                    <Button
                        type="primary"
                        size="large"
                        icon={<PlusOutlined />}
                        onClick={() => form.submit()}
                        loading={loading}
                        block
                    >
                        Create Task
                    </Button>
                </Space>
            </Card>
        </div>
    );
};

export default TaskCreationForm;
