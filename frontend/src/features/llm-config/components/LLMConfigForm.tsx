/**
 * LLM Configuration Form Component
 * Inspired by Flowith 2.0 design principles
 */

import React, { useState, useEffect } from 'react';
import {
    Form,
    Input,
    Select,
    Switch,
    Button,
    Card,
    Space,
    Typography,
    Divider,
    InputNumber,
    Alert,
    Tooltip,
    Collapse,
    Badge,
    message
} from 'antd';
import {
    SaveOutlined,
    DisconnectOutlined,
    EyeInvisibleOutlined,
    EyeOutlined,
    InfoCircleOutlined,
    SettingOutlined,
    ApiOutlined
} from '@ant-design/icons';

import { LLMConfiguration, LLMProvider, CreateLLMConfigRequest } from '../types';
import { useLLMProviders } from '../hooks/useLLMConfig';
import { llmConfigService } from '../services/llmConfigApi';

const { Text, Title } = Typography;
const { Panel } = Collapse;
const { TextArea } = Input;

interface LLMConfigFormProps {
    initialConfig?: LLMConfiguration;
    onSave: (config: LLMConfiguration) => void;
    onCancel: () => void;
    mode: 'create' | 'edit';
}

const LLMConfigForm: React.FC<LLMConfigFormProps> = ({
    initialConfig,
    onSave,
    onCancel,
    mode
}) => {
    const [form] = Form.useForm();
    const { providers, loading: providersLoading } = useLLMProviders();

    const [loading, setLoading] = useState(false);
    const [testing, setTesting] = useState(false);
    const [selectedProvider, setSelectedProvider] = useState<LLMProvider | null>(null);
    const [selectedModel, setSelectedModel] = useState<any>(null);
    const [showApiKey, setShowApiKey] = useState(false);
    const [customHeaders, setCustomHeaders] = useState<string>('{}');
    const [models, setModels] = useState<any[]>([]);
    const [loadingModels, setLoadingModels] = useState(false);

    // Initialize form with existing config
    useEffect(() => {
        if (initialConfig && mode === 'edit') {
            const provider = providers.find(p => p.id === initialConfig.providerId);
            setSelectedProvider(provider || null);

            form.setFieldsValue({
                name: initialConfig.name,
                providerId: initialConfig.providerId,
                modelId: initialConfig.modelId,
                apiKey: initialConfig.apiKey,
                baseUrl: initialConfig.baseUrl,
                isDefault: initialConfig.isDefault,
                isActive: initialConfig.isActive,
                ...initialConfig.parameters
            });

            setCustomHeaders(JSON.stringify(initialConfig.customHeaders || {}, null, 2));
        }
    }, [initialConfig, mode, providers, form]);

    // Load models when provider changes
    useEffect(() => {
        if (selectedProvider && selectedProvider.models.length === 0) {
            loadProviderModels(selectedProvider.id);
        } else if (selectedProvider) {
            setModels(selectedProvider.models);
        }
    }, [selectedProvider]);

    const loadProviderModels = async (providerId: string) => {
        setLoadingModels(true);
        try {
            const providerModels = await llmConfigService.getProviderModels(providerId);
            setModels(providerModels);
        } catch (error) {
            message.error('Failed to load models for provider');
            setModels([]);
        } finally {
            setLoadingModels(false);
        }
    };

    const handleProviderChange = (providerId: string) => {
        const provider = providers.find(p => p.id === providerId);
        setSelectedProvider(provider || null);
        setSelectedModel(null);
        form.setFieldValue('modelId', undefined);

        // Reset provider-specific fields
        if (provider) {
            form.setFieldsValue({
                baseUrl: provider.baseUrl || '',
            });
        }
    };

    const handleModelChange = (modelId: string) => {
        const model = models.find(m => m.id === modelId);
        setSelectedModel(model || null);
    };

    const handleTest = async () => {
        try {
            const values = await form.validateFields();
            setTesting(true);

            // Create a temporary config for testing
            const testConfig: CreateLLMConfigRequest = {
                name: values.name,
                providerId: values.providerId,
                modelId: values.modelId,
                apiKey: values.apiKey,
                baseUrl: values.baseUrl,
                customHeaders: customHeaders ? JSON.parse(customHeaders) : {},
                parameters: getParameterValues(values)
            };

            // For edit mode, update existing config
            let configId = initialConfig?.id;

            if (!configId) {
                // Create temporary config for testing
                const tempConfig = await llmConfigService.createConfiguration({
                    ...testConfig,
                    name: `temp-test-${Date.now()}`
                });
                configId = tempConfig.id;

                // Test and then delete
                try {
                    const result = await llmConfigService.testConfiguration(configId);
                    await llmConfigService.deleteConfiguration(configId);

                    if (result.success) {
                        message.success(`Test successful! Response received in ${result.latency}ms`);
                    } else {
                        message.error(`Test failed: ${result.error}`);
                    }
                } catch (error) {
                    await llmConfigService.deleteConfiguration(configId);
                    throw error;
                }
            } else {
                const result = await llmConfigService.testConfiguration(configId, {
                    prompt: 'This is a test message to verify the configuration is working.'
                });

                if (result.success) {
                    message.success(`Test successful! Response received in ${result.latency}ms`);
                } else {
                    message.error(`Test failed: ${result.error}`);
                }
            }
        } catch (error) {
            message.error('Test failed: ' + (error instanceof Error ? error.message : 'Unknown error'));
        } finally {
            setTesting(false);
        }
    };

    const getParameterValues = (values: any) => {
        const parameters: Record<string, any> = {};

        if (selectedModel?.parameters) {
            selectedModel.parameters.forEach((param: any) => {
                if (values[param.name] !== undefined) {
                    parameters[param.name] = values[param.name];
                }
            });
        }

        return parameters;
    };

    const handleSave = async () => {
        try {
            const values = await form.validateFields();
            setLoading(true);

            const configData = {
                name: values.name,
                providerId: values.providerId,
                modelId: values.modelId,
                apiKey: values.apiKey,
                baseUrl: values.baseUrl,
                customHeaders: customHeaders ? JSON.parse(customHeaders) : {},
                parameters: getParameterValues(values),
                isDefault: values.isDefault || false,
                isActive: values.isActive !== false
            };

            let result: LLMConfiguration;

            if (mode === 'create') {
                result = await llmConfigService.createConfiguration(configData);
                message.success('Configuration created successfully!');
            } else if (initialConfig) {
                result = await llmConfigService.updateConfiguration(initialConfig.id, configData);
                message.success('Configuration updated successfully!');
            } else {
                throw new Error('Invalid mode or missing config');
            }

            onSave(result);
        } catch (error) {
            console.error('Save error:', error);
            message.error('Failed to save configuration: ' + (error instanceof Error ? error.message : 'Unknown error'));
        } finally {
            setLoading(false);
        }
    };

    const renderParameterField = (parameter: any) => {
        const commonProps = {
            label: (
                <Space>
                    {parameter.displayName}
                    {parameter.description && (
                        <Tooltip title={parameter.description}>
                            <InfoCircleOutlined style={{ color: '#8c8c8c' }} />
                        </Tooltip>
                    )}
                </Space>
            ),
            name: parameter.name,
            required: parameter.required,
            extra: parameter.description
        };

        switch (parameter.type) {
            case 'number':
            case 'range':
                return (
                    <Form.Item key={parameter.name} {...commonProps}>
                        <InputNumber
                            min={parameter.min}
                            max={parameter.max}
                            step={parameter.step || 0.1}
                            style={{ width: '100%' }}
                            placeholder={`Default: ${parameter.defaultValue}`}
                        />
                    </Form.Item>
                );

            case 'boolean':
                return (
                    <Form.Item
                        key={parameter.name}
                        {...commonProps}
                        valuePropName="checked"
                        initialValue={parameter.defaultValue}
                    >
                        <Switch />
                    </Form.Item>
                );

            case 'select':
                return (
                    <Form.Item key={parameter.name} {...commonProps}>
                        <Select placeholder={`Default: ${parameter.defaultValue}`}>
                            {parameter.options?.map((option: any) => (
                                <Select.Option key={option.value} value={option.value}>
                                    {option.label}
                                </Select.Option>
                            ))}
                        </Select>
                    </Form.Item>
                );

            default:
                return (
                    <Form.Item key={parameter.name} {...commonProps}>
                        <Input placeholder={`Default: ${parameter.defaultValue}`} />
                    </Form.Item>
                );
        }
    };

    return (
        <Card>
            <Form
                form={form}
                layout="vertical"
                initialValues={{
                    isActive: true,
                    isDefault: false
                }}
            >
                <Space direction="vertical" size="large" style={{ width: '100%' }}>
                    {/* Header */}
                    <div>
                        <Title level={4}>
                            <ApiOutlined /> {mode === 'create' ? 'Add New' : 'Edit'} LLM Configuration
                        </Title>
                        <Text type="secondary">
                            Configure your Large Language Model provider and settings
                        </Text>
                    </div>

                    {/* Basic Configuration */}
                    <Card size="small" title={<><SettingOutlined /> Basic Configuration</>}>
                        <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                            <Form.Item
                                label="Configuration Name"
                                name="name"
                                rules={[{ required: true, message: 'Please enter a configuration name' }]}
                            >
                                <Input placeholder="e.g., GPT-4 Production, Claude Dev, etc." />
                            </Form.Item>

                            <Form.Item
                                label="Provider"
                                name="providerId"
                                rules={[{ required: true, message: 'Please select a provider' }]}
                            >
                                <Select
                                    placeholder="Select LLM Provider"
                                    loading={providersLoading}
                                    onChange={handleProviderChange}
                                >
                                    {providers.map(provider => (
                                        <Select.Option key={provider.id} value={provider.id}>
                                            <Space>
                                                <Badge status={provider.type === 'custom' ? 'warning' : 'success'} />
                                                {provider.displayName}
                                            </Space>
                                        </Select.Option>
                                    ))}
                                </Select>
                            </Form.Item>

                            {selectedProvider && (
                                <Alert
                                    message={selectedProvider.displayName}
                                    description={selectedProvider.description}
                                    type="info"
                                    showIcon
                                    style={{ marginBottom: 16 }}
                                />
                            )}

                            {selectedProvider && (
                                <Form.Item
                                    label="Model"
                                    name="modelId"
                                    rules={[{ required: true, message: 'Please select a model' }]}
                                >
                                    <Select
                                        placeholder="Select Model"
                                        loading={loadingModels}
                                        onChange={handleModelChange}
                                    >
                                        {models.map(model => (
                                            <Select.Option key={model.id} value={model.id}>
                                                <div>
                                                    <div>{model.displayName}</div>
                                                    {model.description && (
                                                        <Text type="secondary" style={{ fontSize: '12px' }}>
                                                            {model.description}
                                                        </Text>
                                                    )}
                                                </div>
                                            </Select.Option>
                                        ))}
                                    </Select>
                                </Form.Item>
                            )}
                        </Space>
                    </Card>

                    {/* Authentication */}
                    {selectedProvider?.requiresApiKey && (
                        <Card size="small" title="Authentication">
                            <Form.Item
                                label={
                                    <Space>
                                        API Key
                                        <Button
                                            type="text"
                                            size="small"
                                            icon={showApiKey ? <EyeInvisibleOutlined /> : <EyeOutlined />}
                                            onClick={() => setShowApiKey(!showApiKey)}
                                        />
                                    </Space>
                                }
                                name="apiKey"
                                rules={[{ required: true, message: 'API Key is required for this provider' }]}
                            >
                                <Input.Password
                                    placeholder="Enter your API key"
                                    visibilityToggle={false}
                                    type={showApiKey ? 'text' : 'password'}
                                />
                            </Form.Item>

                            {selectedProvider.baseUrl && (
                                <Form.Item
                                    label="Base URL"
                                    name="baseUrl"
                                    extra="Override the default API endpoint"
                                >
                                    <Input placeholder={selectedProvider.baseUrl} />
                                </Form.Item>
                            )}
                        </Card>
                    )}

                    {/* Model Parameters */}
                    {selectedModel?.parameters && selectedModel.parameters.length > 0 && (
                        <Collapse>
                            <Panel header={<><SettingOutlined /> Model Parameters</>} key="parameters">
                                <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                                    {selectedModel.parameters.map(renderParameterField)}
                                </Space>
                            </Panel>
                        </Collapse>
                    )}

                    {/* Advanced Settings */}
                    <Collapse>
                        <Panel header="Advanced Settings" key="advanced">
                            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                                <Form.Item
                                    label="Custom Headers"
                                    extra="JSON format for additional headers"
                                >
                                    <TextArea
                                        value={customHeaders}
                                        onChange={(e) => setCustomHeaders(e.target.value)}
                                        placeholder='{"Authorization": "Bearer token", "Custom-Header": "value"}'
                                        rows={4}
                                    />
                                </Form.Item>

                                <Space size="large">
                                    <Form.Item
                                        label="Set as Default"
                                        name="isDefault"
                                        valuePropName="checked"
                                    >
                                        <Switch />
                                    </Form.Item>

                                    <Form.Item
                                        label="Active"
                                        name="isActive"
                                        valuePropName="checked"
                                    >
                                        <Switch />
                                    </Form.Item>
                                </Space>
                            </Space>
                        </Panel>
                    </Collapse>

                    {/* Actions */}
                    <Divider />
                    <Space>
                        <Button onClick={onCancel}>
                            Cancel
                        </Button>
                        <Button
                            icon={<DisconnectOutlined />}
                            onClick={handleTest}
                            loading={testing}
                            disabled={!selectedProvider || !form.getFieldValue('modelId')}
                        >
                            Test Connection
                        </Button>
                        <Button
                            type="primary"
                            icon={<SaveOutlined />}
                            onClick={handleSave}
                            loading={loading}
                        >
                            {mode === 'create' ? 'Create' : 'Update'} Configuration
                        </Button>
                    </Space>
                </Space>
            </Form>
        </Card>
    );
};

export default LLMConfigForm;
