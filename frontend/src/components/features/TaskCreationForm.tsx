import React, { useState } from 'react';
import {
    Form,
    Input,
    Select,
    Button,
    Card,
    Space,
    Typography,
    Divider,
    Alert
} from 'antd';
import {
    PlusOutlined,
    RocketOutlined,
    BulbOutlined,
    TeamOutlined,
    UserOutlined,
    ApiOutlined
} from '@ant-design/icons';
import { taskApi } from '../../services/api';
import type { UploadedDocument, ComplexityAnalysis, TaskCreateRequest } from '../../types';
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
    const [uploadedDocuments, setUploadedDocuments] = useState<UploadedDocument[]>([]);
    const [complexityAnalysis, setComplexityAnalysis] = useState<ComplexityAnalysis | null>(null);
    const [analyzingComplexity, setAnalyzingComplexity] = useState(false);

    const complexityOptions = [
        { value: 'low', label: 'Low - Simple tasks, quick execution', icon: <UserOutlined /> },
        { value: 'medium', label: 'Medium - Moderate complexity, may require multiple steps', icon: <BulbOutlined /> },
        { value: 'high', label: 'High - Complex tasks, multi-agent coordination', icon: <TeamOutlined /> },
    ];

    const modeOptions = [
        { value: 'auto', label: 'Auto - Let AI decide the best approach', icon: <ApiOutlined /> },
        { value: 'single', label: 'Single Agent - Use one specialized agent', icon: <UserOutlined /> },
        { value: 'multi', label: 'Multi-Agent - Coordinate multiple agents', icon: <TeamOutlined /> },
    ];

    const handleUploadSuccess = (files: UploadedDocument[]) => {
        setUploadedDocuments(prev => [...prev, ...files]);
    };

    const analyzeTaskComplexity = async (description: string) => {
        if (!description.trim() || description.length < 10) return;

        setAnalyzingComplexity(true);
        try {
            const analysis = await taskApi.analyzeComplexity(description);
            setComplexityAnalysis(analysis);

            // Auto-set recommended values
            form.setFieldsValue({
                complexity: analysis.isComplex ? 'high' : 'medium',
                mode: analysis.recommendation,
            });
        } catch (error) {
            console.error('Error analyzing complexity:', error);
        } finally {
            setAnalyzingComplexity(false);
        }
    };

    const handleDescriptionChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const description = e.target.value;
        // Debounce analysis
        setTimeout(() => {
            analyzeTaskComplexity(description);
        }, 1500);
    };

    const handleSubmit = async (values: any) => {
        setLoading(true);

        try {
            const taskData: TaskCreateRequest = {
                title: values.title,
                description: values.description,
                complexity: values.complexity,
                priority: values.priority || 'medium',
                document_ids: uploadedDocuments.map(doc => doc.id),
                tags: values.tags ? values.tags.split(',').map((tag: string) => tag.trim()) : [],
            };

            const response = await taskApi.createTask(taskData);

            if (onTaskCreated) {
                onTaskCreated(response.task.id);
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
                                onChange={handleDescriptionChange}
                            />
                        </Form.Item>

                        {complexityAnalysis && (
                            <Alert
                                message={`Complexity Analysis: ${complexityAnalysis.isComplex ? 'High' : 'Medium'} complexity detected`}
                                description={`Recommended mode: ${complexityAnalysis.recommendation}-agent approach`}
                                type="info"
                                showIcon
                                style={{ marginBottom: '16px' }}
                            />
                        )}

                        {analyzingComplexity && (
                            <Alert
                                message="Analyzing task complexity..."
                                type="info"
                                showIcon
                                style={{ marginBottom: '16px' }}
                            />
                        )}

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
                            label="Execution Mode"
                            name="mode"
                            initialValue="auto"
                        >
                            <Select placeholder="Select execution mode" size="large">
                                {modeOptions.map(option => (
                                    <Option key={option.value} value={option.value}>
                                        <Space>
                                            {option.icon}
                                            {option.label}
                                        </Space>
                                    </Option>
                                ))}
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
                                            <Text strong>{doc.name}</Text>
                                            <br />
                                            <Text type="secondary" style={{ fontSize: '12px' }}>
                                                {doc.type} • {(doc.size / 1024 / 1024).toFixed(2)} MB
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
