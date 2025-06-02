/**
 * LLM Configuration List Component
 * Displays and manages all LLM configurations
 */

import React, { useState } from 'react';
import {
    Table,
    Card,
    Space,
    Typography,
    Button,
    Tag,
    Dropdown,
    Modal,
    message,
    Tooltip,
    Badge,
    Statistic,
    Empty,
    Result,
    Spin
} from 'antd';
import type { ColumnsType, TableProps } from 'antd/es/table';
import {
    PlusOutlined,
    EditOutlined,
    DeleteOutlined,
    DisconnectOutlined,
    MoreOutlined,
    StarOutlined,
    StarFilled,
    PlayCircleOutlined,
    PauseCircleOutlined,
    ApiOutlined
} from '@ant-design/icons';

import { LLMConfiguration } from '../types';
import { useLLMConfigurations, useLLMTesting } from '../hooks/useLLMConfig';
import LLMConfigForm from './LLMConfigForm';

const { Title, Text } = Typography;

interface LLMConfigListProps {
    onConfigSelect?: (config: LLMConfiguration) => void;
}

const LLMConfigList: React.FC<LLMConfigListProps> = ({ onConfigSelect }) => {
    const { configurations, loading, actions } = useLLMConfigurations();
    const { testConfiguration, testResults } = useLLMTesting();

    const [modalVisible, setModalVisible] = useState(false);
    const [editingConfig, setEditingConfig] = useState<LLMConfiguration | null>(null);
    const [testingConfig, setTestingConfig] = useState<string | null>(null);

    const handleCreate = () => {
        setEditingConfig(null);
        setModalVisible(true);
    };

    const handleEdit = (config: LLMConfiguration) => {
        setEditingConfig(config);
        setModalVisible(true);
    };

    const handleDelete = (config: LLMConfiguration) => {
        Modal.confirm({
            title: 'Delete Configuration',
            content: `Are you sure you want to delete "${config.name}"? This action cannot be undone.`,
            okType: 'danger',
            onOk: async () => {
                try {
                    await actions.delete(config.id);
                    message.success('Configuration deleted successfully');
                } catch (error) {
                    message.error('Failed to delete configuration');
                }
            }
        });
    };

    const handleSetDefault = async (config: LLMConfiguration) => {
        try {
            await actions.setDefault(config.id);
            message.success(`"${config.name}" set as default configuration`);
        } catch (error) {
            message.error('Failed to set default configuration');
        }
    };

    const handleToggleActive = async (config: LLMConfiguration) => {
        try {
            await actions.toggle(config.id, !config.isActive);
            message.success(`Configuration ${config.isActive ? 'deactivated' : 'activated'}`);
        } catch (error) {
            message.error('Failed to toggle configuration');
        }
    };

    const handleTest = async (config: LLMConfiguration) => {
        setTestingConfig(config.id);
        try {
            const result = await testConfiguration(config.id);
            if (result.success) {
                message.success(`Test successful! Latency: ${result.latency}ms`);
            } else {
                message.error(`Test failed: ${result.error}`);
            }
        } catch (error) {
            message.error('Test failed');
        } finally {
            setTestingConfig(null);
        }
    };

    const handleSave = () => {
        setModalVisible(false);
        setEditingConfig(null);
        actions.refetch();
    };

    const getProviderName = (providerId: string) => {
        // This would use the provider hook, but for simplicity showing ID
        return providerId;
    };

    const getStatusColor = (isActive: boolean) => {
        return isActive ? 'success' : 'default';
    };

    const getStatusText = (isActive: boolean) => {
        return isActive ? 'Active' : 'Inactive';
    };

    const getTestStatus = (configId: string) => {
        const result = testResults[configId];
        if (!result) return null;

        return result.success ? (
            <Badge status="success" text={`${result.latency}ms`} />
        ) : (
            <Badge status="error" text="Failed" />
        );
    };

    const columns: ColumnsType<LLMConfiguration> = [
        {
            title: 'Name',
            dataIndex: 'name',
            key: 'name',
            render: (text, record) => (
                <Space>
                    <Text strong>{text}</Text>
                    {record.isDefault && (
                        <Tooltip title="Default Configuration">
                            <StarFilled style={{ color: '#faad14' }} />
                        </Tooltip>
                    )}
                </Space>
            ),
        },
        {
            title: 'Provider',
            dataIndex: 'providerId',
            key: 'provider',
            render: (providerId) => (
                <Tag color="blue">{getProviderName(providerId)}</Tag>
            ),
        },
        {
            title: 'Model',
            dataIndex: 'modelId',
            key: 'model',
            render: (modelId) => <Text code>{modelId}</Text>,
        },
        {
            title: 'Status',
            dataIndex: 'isActive',
            key: 'status',
            render: (isActive) => (
                <Tag color={getStatusColor(isActive)}>
                    {getStatusText(isActive)}
                </Tag>
            ),
        },
        {
            title: 'Last Test',
            key: 'lastTest',
            render: (_, record) => getTestStatus(record.id) || <Text type="secondary">Not tested</Text>,
        },
        {
            title: 'Updated',
            dataIndex: 'updatedAt',
            key: 'updatedAt',
            render: (date) => new Date(date).toLocaleDateString(),
        },
        {
            title: 'Actions',
            key: 'actions',
            render: (_, record) => (
                <Space>
                    <Tooltip title="Test Configuration">
                        <Button
                            type="text"
                            icon={<DisconnectOutlined />}
                            onClick={() => handleTest(record)}
                            loading={testingConfig === record.id}
                            size="small"
                        />
                    </Tooltip>

                    <Dropdown
                        menu={{
                            items: [
                                {
                                    key: 'edit',
                                    label: 'Edit',
                                    icon: <EditOutlined />,
                                    onClick: () => handleEdit(record)
                                },
                                {
                                    key: 'setDefault',
                                    label: record.isDefault ? 'Default' : 'Set as Default',
                                    icon: record.isDefault ? <StarFilled /> : <StarOutlined />,
                                    disabled: record.isDefault,
                                    onClick: () => handleSetDefault(record)
                                },
                                {
                                    key: 'toggle',
                                    label: record.isActive ? 'Deactivate' : 'Activate',
                                    icon: record.isActive ? <PauseCircleOutlined /> : <PlayCircleOutlined />,
                                    onClick: () => handleToggleActive(record)
                                },
                                { type: 'divider' },
                                {
                                    key: 'delete',
                                    label: 'Delete',
                                    icon: <DeleteOutlined />,
                                    danger: true,
                                    onClick: () => handleDelete(record)
                                }
                            ]
                        }}
                        trigger={['click']}
                    >
                        <Button type="text" icon={<MoreOutlined />} size="small" />
                    </Dropdown>
                </Space>
            ),
        },
    ];

    const tableProps: TableProps<LLMConfiguration> = {
        columns,
        dataSource: configurations,
        rowKey: 'id',
        loading,
        pagination: {
            pageSize: 10,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} configurations`,
        },
        onRow: (record) => ({
            onClick: () => onConfigSelect?.(record),
            style: { cursor: onConfigSelect ? 'pointer' : 'default' }
        })
    };

    // Statistics
    const totalConfigs = configurations.length;
    const activeConfigs = configurations.filter(c => c.isActive).length;
    const defaultConfig = configurations.find(c => c.isDefault);

    return (
        <div>
            {/* Header with Stats */}
            <Card style={{ marginBottom: 16 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                        <Title level={4} style={{ margin: 0 }}>
                            <ApiOutlined /> LLM Configurations
                        </Title>
                        <Text type="secondary">
                            Manage your Large Language Model configurations
                        </Text>
                    </div>

                    <Space size="large">
                        <Statistic
                            title="Total"
                            value={totalConfigs}
                            prefix={<ApiOutlined />}
                        />
                        <Statistic
                            title="Active"
                            value={activeConfigs}
                            valueStyle={{ color: '#3f8600' }}
                            prefix={<PlayCircleOutlined />}
                        />
                        <Button
                            type="primary"
                            icon={<PlusOutlined />}
                            onClick={handleCreate}
                        >
                            Add Configuration
                        </Button>
                    </Space>
                </div>
            </Card>

            {/* Default Configuration Info */}
            {defaultConfig && (
                <Card size="small" style={{ marginBottom: 16, backgroundColor: '#f6ffed' }}>
                    <Space>
                        <StarFilled style={{ color: '#faad14' }} />
                        <Text>
                            <Text strong>{defaultConfig.name}</Text> is set as the default configuration
                        </Text>
                        <Text type="secondary">
                            ({defaultConfig.providerId} - {defaultConfig.modelId})
                        </Text>
                    </Space>
                </Card>
            )}

            {/* Configurations Table */}
            <Card>
                {loading ? (
                    <div style={{ textAlign: 'center', padding: '40px 0' }}>
                        <Spin size="large" />
                    </div>
                ) : configurations.length > 0 ? (
                    <Table {...tableProps} />
                ) : (
                    <Empty
                        description={
                            <Result
                                status="404"
                                title="No Configurations Found"
                                subTitle="It looks like you don't have any LLM configurations yet."
                                extra={
                                    <Button type="primary" icon={<PlusOutlined />} onClick={handleCreate}>
                                        Create Configuration
                                    </Button>
                                }
                            />
                        }
                    />
                )}
            </Card>

            {/* Configuration Form Modal */}
            <Modal
                title={editingConfig ? 'Edit Configuration' : 'Add New Configuration'}
                open={modalVisible}
                onCancel={() => setModalVisible(false)}
                footer={null}
                width={800}
                destroyOnClose
            >
                <LLMConfigForm
                    initialConfig={editingConfig || undefined}
                    onSave={handleSave}
                    onCancel={() => setModalVisible(false)}
                    mode={editingConfig ? 'edit' : 'create'}
                />
            </Modal>
        </div>
    );
};

export default LLMConfigList;
