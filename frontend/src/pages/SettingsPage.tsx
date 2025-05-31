import React, { useState } from 'react';
import {
    Card,
    Form,
    Switch,
    Button,
    Space,
    Typography,
    Divider,
    message,
    InputNumber,
    Select
} from 'antd';
import { SaveOutlined, ReloadOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;
const { Option } = Select;

interface SettingsFormData {
    maxConcurrentTasks: number;
    enableNotifications: boolean;
    notificationSound: boolean;
    autoRefreshInterval: number;
    defaultComplexity: string;
    defaultPriority: string;
    maxFileSize: number;
    apiTimeout: number;
    logLevel: string;
}

const SettingsPage: React.FC = () => {
    const [form] = Form.useForm<SettingsFormData>();
    const [loading, setLoading] = useState(false);

    const handleSave = async (values: SettingsFormData) => {
        setLoading(true);
        try {
            // In a real app, this would save to backend
            localStorage.setItem('openmanus-settings', JSON.stringify(values));
            message.success('Settings saved successfully!');
        } catch (error) {
            message.error('Failed to save settings');
        } finally {
            setLoading(false);
        }
    };

    const handleReset = () => {
        form.setFieldsValue({
            maxConcurrentTasks: 5,
            enableNotifications: true,
            notificationSound: true,
            autoRefreshInterval: 5000,
            defaultComplexity: 'medium',
            defaultPriority: 'medium',
            maxFileSize: 50,
            apiTimeout: 30000,
            logLevel: 'info',
        });
        message.info('Settings reset to defaults');
    };

    const initialValues: SettingsFormData = {
        maxConcurrentTasks: 5,
        enableNotifications: true,
        notificationSound: true,
        autoRefreshInterval: 5000,
        defaultComplexity: 'medium',
        defaultPriority: 'medium',
        maxFileSize: 50,
        apiTimeout: 30000,
        logLevel: 'info',
    };

    return (
        <div style={{ padding: '24px', marginLeft: '250px' }}>
            <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                <Space direction="vertical" style={{ width: '100%' }} size="large">
                    <div>
                        <Title level={2}>Settings</Title>
                        <Text type="secondary">
                            Configure your OpenManus experience
                        </Text>
                    </div>

                    <Form
                        form={form}
                        layout="vertical"
                        initialValues={initialValues}
                        onFinish={handleSave}
                    >
                        {/* General Settings */}
                        <Card title="General Settings">
                            <Space direction="vertical" style={{ width: '100%' }} size="middle">
                                <Form.Item
                                    label="Maximum Concurrent Tasks"
                                    name="maxConcurrentTasks"
                                    help="Maximum number of tasks that can run simultaneously"
                                >
                                    <InputNumber
                                        min={1}
                                        max={20}
                                        style={{ width: '200px' }}
                                    />
                                </Form.Item>

                                <Form.Item
                                    label="Auto Refresh Interval"
                                    name="autoRefreshInterval"
                                    help="How often to refresh task status (in milliseconds)"
                                >
                                    <InputNumber
                                        min={1000}
                                        max={60000}
                                        step={1000}
                                        style={{ width: '200px' }}
                                    />
                                </Form.Item>

                                <Form.Item
                                    label="API Timeout"
                                    name="apiTimeout"
                                    help="Request timeout for API calls (in milliseconds)"
                                >
                                    <InputNumber
                                        min={5000}
                                        max={120000}
                                        step={5000}
                                        style={{ width: '200px' }}
                                    />
                                </Form.Item>
                            </Space>
                        </Card>

                        {/* Task Defaults */}
                        <Card title="Task Defaults">
                            <Space direction="vertical" style={{ width: '100%' }} size="middle">
                                <Form.Item
                                    label="Default Complexity"
                                    name="defaultComplexity"
                                    help="Default complexity level for new tasks"
                                >
                                    <Select style={{ width: '200px' }}>
                                        <Option value="low">Low</Option>
                                        <Option value="medium">Medium</Option>
                                        <Option value="high">High</Option>
                                    </Select>
                                </Form.Item>

                                <Form.Item
                                    label="Default Priority"
                                    name="defaultPriority"
                                    help="Default priority level for new tasks"
                                >
                                    <Select style={{ width: '200px' }}>
                                        <Option value="low">Low</Option>
                                        <Option value="medium">Medium</Option>
                                        <Option value="high">High</Option>
                                        <Option value="urgent">Urgent</Option>
                                    </Select>
                                </Form.Item>
                            </Space>
                        </Card>

                        {/* File Upload Settings */}
                        <Card title="File Upload Settings">
                            <Form.Item
                                label="Maximum File Size"
                                name="maxFileSize"
                                help="Maximum file size for uploads (in MB)"
                            >
                                <InputNumber
                                    min={1}
                                    max={500}
                                    style={{ width: '200px' }}
                                    formatter={value => `${value} MB`}
                                    parser={value => parseInt(value!.replace(' MB', ''), 10) as 1 | 500}
                                />
                            </Form.Item>
                        </Card>

                        {/* Notifications */}
                        <Card title="Notifications">
                            <Space direction="vertical" style={{ width: '100%' }} size="middle">
                                <Form.Item
                                    label="Enable Notifications"
                                    name="enableNotifications"
                                    valuePropName="checked"
                                    help="Receive notifications about task updates"
                                >
                                    <Switch />
                                </Form.Item>

                                <Form.Item
                                    label="Notification Sound"
                                    name="notificationSound"
                                    valuePropName="checked"
                                    help="Play sound with notifications"
                                >
                                    <Switch />
                                </Form.Item>
                            </Space>
                        </Card>

                        {/* Advanced Settings */}
                        <Card title="Advanced Settings">
                            <Form.Item
                                label="Log Level"
                                name="logLevel"
                                help="Logging level for debugging"
                            >
                                <Select style={{ width: '200px' }}>
                                    <Option value="error">Error</Option>
                                    <Option value="warn">Warning</Option>
                                    <Option value="info">Info</Option>
                                    <Option value="debug">Debug</Option>
                                </Select>
                            </Form.Item>
                        </Card>

                        <Divider />

                        {/* Action Buttons */}
                        <Space>
                            <Button
                                type="primary"
                                icon={<SaveOutlined />}
                                htmlType="submit"
                                loading={loading}
                                size="large"
                            >
                                Save Settings
                            </Button>
                            <Button
                                icon={<ReloadOutlined />}
                                onClick={handleReset}
                                size="large"
                            >
                                Reset to Defaults
                            </Button>
                        </Space>
                    </Form>
                </Space>
            </div>
        </div>
    );
};

export default SettingsPage;
