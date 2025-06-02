import React, { useState, useCallback, useEffect } from 'react';
import { Card, Input, Typography, Space, Badge, Tooltip } from 'antd';
import { Handle, Position, NodeProps } from 'reactflow';
import {
    EditOutlined,
    MessageOutlined,
    CheckCircleOutlined,
    CloseCircleOutlined,
    LoadingOutlined,
    ExclamationCircleOutlined
} from '@ant-design/icons';
import { useCanvasStore } from '../../store/canvasStore';

const { TextArea } = Input;
const { Text } = Typography;

interface PromptNodeData {
    label: string;
    prompt: string;
    description?: string;
    status?: 'idle' | 'running' | 'completed' | 'failed';
    result?: string;
    error?: string;
    editable?: boolean;
    placeholder?: string;
}

interface PromptNodeProps extends NodeProps {
    data: PromptNodeData;
}

const PromptNode: React.FC<PromptNodeProps> = ({ id, data, selected }) => {
    const [isEditing, setIsEditing] = useState(false);
    const [promptText, setPromptText] = useState(data.prompt || '');
    const [localLabel, setLocalLabel] = useState(data.label || 'Prompt');

    const updateNode = useCanvasStore(state => state.updateNode);

    // Handle prompt text changes
    const handlePromptChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setPromptText(e.target.value);
    }, []);

    // Handle blur event to save changes
    const handlePromptBlur = useCallback(() => {
        setIsEditing(false);
        if (promptText !== data.prompt) {
            updateNode(id, { prompt: promptText });
        }
    }, [id, promptText, data.prompt, updateNode]);

    // Handle label changes
    const handleLabelChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
        const newLabel = e.target.value;
        setLocalLabel(newLabel);
        updateNode(id, { label: newLabel });
    }, [id, updateNode]);

    // Handle enter key in prompt area
    const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && e.ctrlKey) {
            handlePromptBlur();
        }
        if (e.key === 'Escape') {
            setPromptText(data.prompt || '');
            setIsEditing(false);
        }
    }, [handlePromptBlur, data.prompt]);

    // Update local state when data changes
    useEffect(() => {
        setPromptText(data.prompt || '');
        setLocalLabel(data.label || 'Prompt');
    }, [data.prompt, data.label]);

    // Get status icon and color
    const getStatusDisplay = () => {
        switch (data.status) {
            case 'running':
                return {
                    icon: <LoadingOutlined spin style={{ color: '#1890ff' }} />,
                    color: '#1890ff',
                    text: 'Processing'
                };
            case 'completed':
                return {
                    icon: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
                    color: '#52c41a',
                    text: 'Completed'
                };
            case 'failed':
                return {
                    icon: <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
                    color: '#ff4d4f',
                    text: 'Failed'
                };
            default:
                return {
                    icon: <MessageOutlined style={{ color: '#d9d9d9' }} />,
                    color: '#d9d9d9',
                    text: 'Ready'
                };
        }
    };

    const statusDisplay = getStatusDisplay();
    const editable = data.editable !== false; // Default to true

    return (
        <div style={{ minWidth: '300px', maxWidth: '400px' }}>
            {/* Input Handle */}
            <Handle
                type="target"
                position={Position.Left}
                style={{
                    background: '#555',
                    width: '12px',
                    height: '12px',
                    border: '2px solid #fff'
                }}
                isConnectable={true}
            />

            {/* Node Content */}
            <Card
                size="small"
                style={{
                    border: selected ? '2px solid #1890ff' : '1px solid #d9d9d9',
                    borderRadius: '8px',
                    boxShadow: selected
                        ? '0 4px 12px rgba(24, 144, 255, 0.3)'
                        : '0 2px 8px rgba(0, 0, 0, 0.1)',
                    backgroundColor: '#fff'
                }}
                title={
                    <Space style={{ width: '100%', justifyContent: 'space-between' }}>
                        <Space>
                            {statusDisplay.icon}
                            {editable ? (
                                <Input
                                    value={localLabel}
                                    onChange={handleLabelChange}
                                    variant="borderless"
                                    style={{
                                        fontWeight: 'bold',
                                        padding: 0,
                                        fontSize: '14px'
                                    }}
                                    placeholder="Node Label"
                                />
                            ) : (
                                <Text strong>{localLabel}</Text>
                            )}
                        </Space>
                        <Badge
                            color={statusDisplay.color}
                            text={statusDisplay.text}
                            style={{ fontSize: '10px' }}
                        />
                    </Space>
                }
                extra={
                    editable && (
                        <Tooltip title={isEditing ? "Ctrl+Enter to save, Esc to cancel" : "Click to edit"}>
                            <EditOutlined
                                style={{
                                    color: isEditing ? '#1890ff' : '#666',
                                    cursor: 'pointer'
                                }}
                                onClick={() => setIsEditing(true)}
                            />
                        </Tooltip>
                    )
                }
            >
                <Space direction="vertical" style={{ width: '100%' }} size="middle">
                    {/* Description */}
                    {data.description && (
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                            {data.description}
                        </Text>
                    )}

                    {/* Prompt Editor */}
                    <div>
                        <TextArea
                            value={promptText}
                            onChange={handlePromptChange}
                            onBlur={handlePromptBlur}
                            onKeyDown={handleKeyDown}
                            onFocus={() => setIsEditing(true)}
                            placeholder={data.placeholder || "Enter your prompt here..."}
                            autoSize={{ minRows: 3, maxRows: 8 }}
                            disabled={!editable}
                            style={{
                                resize: 'none',
                                fontFamily: 'monospace',
                                fontSize: '13px',
                                border: isEditing ? '1px solid #1890ff' : '1px solid #d9d9d9'
                            }}
                        />
                        {isEditing && (
                            <Text type="secondary" style={{ fontSize: '11px' }}>
                                Ctrl+Enter to save • Esc to cancel
                            </Text>
                        )}
                    </div>

                    {/* Result Display */}
                    {data.result && (
                        <div style={{
                            padding: '8px',
                            backgroundColor: '#f6ffed',
                            border: '1px solid #b7eb8f',
                            borderRadius: '4px'
                        }}>
                            <Text style={{ fontSize: '12px' }}>
                                <strong>Result:</strong> {data.result.substring(0, 100)}
                                {data.result.length > 100 && '...'}
                            </Text>
                        </div>
                    )}

                    {/* Error Display */}
                    {data.error && (
                        <div style={{
                            padding: '8px',
                            backgroundColor: '#fff2f0',
                            border: '1px solid #ffccc7',
                            borderRadius: '4px'
                        }}>
                            <Space>
                                <ExclamationCircleOutlined style={{ color: '#ff4d4f' }} />
                                <Text type="danger" style={{ fontSize: '12px' }}>
                                    {data.error}
                                </Text>
                            </Space>
                        </div>
                    )}

                    {/* Character Count */}
                    <div style={{ textAlign: 'right' }}>
                        <Text type="secondary" style={{ fontSize: '11px' }}>
                            {promptText.length} characters
                        </Text>
                    </div>
                </Space>
            </Card>

            {/* Output Handle */}
            <Handle
                type="source"
                position={Position.Right}
                style={{
                    background: '#555',
                    width: '12px',
                    height: '12px',
                    border: '2px solid #fff'
                }}
                isConnectable={true}
            />
        </div>
    );
};

export default PromptNode;
