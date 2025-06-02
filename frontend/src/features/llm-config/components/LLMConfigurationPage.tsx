/**
 * LLM Configuration Page Component
 * Main page for managing LLM configurations with Flowith-inspired design
 */

import React, { useState } from 'react';
import {
    Card,
    Typography,
    Space,
    Button,
    Row,
    Col,
    Alert,
    Tabs,
    Statistic,
    Badge
} from 'antd';
import {
    ApiOutlined,
    PlusOutlined,
    SettingOutlined,
    ThunderboltOutlined,
    CloudServerOutlined
} from '@ant-design/icons';

import { useLLMConfigurations, useLLMProviders } from '../hooks/useLLMConfig';
import LLMConfigList from './LLMConfigList';
import LLMProviderCard from './LLMProviderCard';
import LLMConfigForm from './LLMConfigForm';

const { Title, Text } = Typography;

const LLMConfigurationPage: React.FC = () => {
    const { configurations, currentConfig, actions } = useLLMConfigurations();
    const { providers } = useLLMProviders();

    const [activeTab, setActiveTab] = useState('configurations');
    const [showCreateForm, setShowCreateForm] = useState(false);

    const handleCreateNew = () => {
        setShowCreateForm(true);
        setActiveTab('create');
    };

    const handleFormSave = () => {
        setShowCreateForm(false);
        setActiveTab('configurations');
        actions.refetch();
    };

    const handleFormCancel = () => {
        setShowCreateForm(false);
        setActiveTab('configurations');
    };

    // Statistics
    const stats = {
        total: configurations.length,
        active: configurations.filter(c => c.isActive).length,
        providers: providers.length,
        hasDefault: configurations.some(c => c.isDefault)
    };

    return (
        <div style={{ padding: '24px', background: '#f5f5f5', minHeight: 'calc(100vh - 64px)' }}>
            <div style={{ maxWidth: '1200px', margin: '0 auto' }}>

                {/* Page Header */}
                <Card style={{ marginBottom: '24px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                            <Title level={2} style={{ margin: 0, display: 'flex', alignItems: 'center', gap: '12px' }}>
                                <CloudServerOutlined style={{ color: '#1890ff' }} />
                                LLM Configuration Center
                            </Title>
                            <Text type="secondary" style={{ fontSize: '16px' }}>
                                Manage your Large Language Model providers and configurations
                            </Text>
                        </div>

                        <Button
                            type="primary"
                            size="large"
                            icon={<PlusOutlined />}
                            onClick={handleCreateNew}
                        >
                            Add Configuration
                        </Button>
                    </div>
                </Card>

                {/* Quick Stats */}
                <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
                    <Col xs={12} sm={6}>
                        <Card>
                            <Statistic
                                title="Total Configurations"
                                value={stats.total}
                                prefix={<ApiOutlined style={{ color: '#1890ff' }} />}
                                valueStyle={{ color: '#1890ff' }}
                            />
                        </Card>
                    </Col>
                    <Col xs={12} sm={6}>
                        <Card>
                            <Statistic
                                title="Active"
                                value={stats.active}
                                prefix={<ThunderboltOutlined style={{ color: '#52c41a' }} />}
                                valueStyle={{ color: '#52c41a' }}
                            />
                        </Card>
                    </Col>
                    <Col xs={12} sm={6}>
                        <Card>
                            <Statistic
                                title="Providers Available"
                                value={stats.providers}
                                prefix={<CloudServerOutlined style={{ color: '#722ed1' }} />}
                                valueStyle={{ color: '#722ed1' }}
                            />
                        </Card>
                    </Col>
                    <Col xs={12} sm={6}>
                        <Card>
                            <div style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '4px' }}>
                                    {stats.hasDefault ? (
                                        <Badge status="success" text="Set" />
                                    ) : (
                                        <Badge status="warning" text="None" />
                                    )}
                                </div>
                                <div style={{ color: '#8c8c8c', fontSize: '14px' }}>
                                    Default Config
                                </div>
                            </div>
                        </Card>
                    </Col>
                </Row>

                {/* Alerts */}
                {!stats.hasDefault && stats.total > 0 && (
                    <Alert
                        message="No Default Configuration Set"
                        description="Set a default LLM configuration to ensure seamless operation across the system."
                        type="warning"
                        showIcon
                        style={{ marginBottom: '24px' }}
                        action={
                            <Button size="small" type="primary" ghost>
                                Set Default
                            </Button>
                        }
                    />
                )}

                {currentConfig && (
                    <Alert
                        message={
                            <Space>
                                <Text>Current Active Configuration:</Text>
                                <Text strong>{currentConfig.name}</Text>
                                <Text type="secondary">
                                    ({currentConfig.providerId} - {currentConfig.modelId})
                                </Text>
                            </Space>
                        }
                        type="info"
                        showIcon
                        style={{ marginBottom: '24px' }}
                    />
                )}

                {/* Main Content Tabs */}
                <Card>
                    <Tabs
                        activeKey={activeTab}
                        onChange={setActiveTab}
                        size="large"
                        items={[
                            {
                                key: 'configurations',
                                label: (
                                    <Space>
                                        <SettingOutlined />
                                        My Configurations
                                        <Badge count={stats.total} style={{ backgroundColor: '#1890ff' }} />
                                    </Space>
                                ),
                                children: (
                                    <LLMConfigList />
                                )
                            },
                            {
                                key: 'providers',
                                label: (
                                    <Space>
                                        <CloudServerOutlined />
                                        Available Providers
                                        <Badge count={stats.providers} style={{ backgroundColor: '#722ed1' }} />
                                    </Space>
                                ),
                                children: (
                                    <div>
                                        <div style={{ marginBottom: '24px' }}>
                                            <Title level={4}>Supported LLM Providers</Title>
                                            <Text type="secondary">
                                                Choose from our supported providers to create new configurations
                                            </Text>
                                        </div>

                                        <Row gutter={[16, 16]}>
                                            {providers.map(provider => (
                                                <Col key={provider.id} xs={24} sm={12} lg={8}>
                                                    <LLMProviderCard
                                                        provider={provider}
                                                        onSelect={() => {
                                                            setActiveTab('create');
                                                            setShowCreateForm(true);
                                                        }}
                                                    />
                                                </Col>
                                            ))}
                                        </Row>
                                    </div>
                                )
                            },
                            {
                                key: 'create',
                                label: (
                                    <Space>
                                        <PlusOutlined />
                                        Add New Configuration
                                    </Space>
                                ),
                                children: showCreateForm ? (
                                    <LLMConfigForm
                                        mode="create"
                                        onSave={handleFormSave}
                                        onCancel={handleFormCancel}
                                    />
                                ) : (
                                    <div style={{ textAlign: 'center', padding: '60px 0' }}>
                                        <ApiOutlined style={{ fontSize: '64px', color: '#d9d9d9', marginBottom: '16px' }} />
                                        <Title level={4} style={{ color: '#8c8c8c' }}>
                                            Ready to Add a New Configuration
                                        </Title>
                                        <Text type="secondary">
                                            Configure a new LLM provider to expand your AI capabilities
                                        </Text>
                                        <div style={{ marginTop: '24px' }}>
                                            <Button
                                                type="primary"
                                                size="large"
                                                icon={<PlusOutlined />}
                                                onClick={() => setShowCreateForm(true)}
                                            >
                                                Start Configuration
                                            </Button>
                                        </div>
                                    </div>
                                )
                            }
                        ]}
                    />
                </Card>
            </div>
        </div>
    );
};

export default LLMConfigurationPage;
