import React, { useState } from 'react';
import {
    Input,
    Button,
    Space,
    Card,
    Typography,
    Collapse,
    Badge,
    Tooltip,
    Affix
} from 'antd';
import {
    SendOutlined,
    SettingOutlined,
    BookOutlined,
    UpOutlined,
    DownOutlined
} from '@ant-design/icons';
import { SourceSelector } from '../../features/knowledge/components';

const { TextArea } = Input;
const { Text } = Typography;
const { Panel } = Collapse;

interface ChatInputProps {
    onSendMessage: (message: string, sourceIds?: string[]) => void;
    loading?: boolean;
    disabled?: boolean;
    placeholder?: string;
}

const ChatInput: React.FC<ChatInputProps> = ({
    onSendMessage,
    loading = false,
    disabled = false,
    placeholder = "Type your message or describe a task..."
}) => {
    const [message, setMessage] = useState('');
    const [selectedSourceIds, setSelectedSourceIds] = useState<string[]>([]);
    const [showKnowledgeContext, setShowKnowledgeContext] = useState(false);

    const handleSend = () => {
        if (message.trim()) {
            onSendMessage(message.trim(), selectedSourceIds.length > 0 ? selectedSourceIds : undefined);
            setMessage('');
            // Keep source selection for convenience
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const toggleKnowledgeContext = () => {
        setShowKnowledgeContext(!showKnowledgeContext);
    };

    const getContextSummary = () => {
        if (selectedSourceIds.length === 0) return null;

        return (
            <div style={{ marginTop: '8px' }}>
                <Space size="small">
                    <BookOutlined style={{ color: '#1890ff', fontSize: '12px' }} />
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                        Using {selectedSourceIds.length} knowledge source{selectedSourceIds.length !== 1 ? 's' : ''} for context
                    </Text>
                    <Button
                        type="link"
                        size="small"
                        onClick={toggleKnowledgeContext}
                        style={{ fontSize: '12px', padding: 0 }}
                    >
                        {showKnowledgeContext ? 'Hide' : 'Manage'}
                    </Button>
                </Space>
            </div>
        );
    };

    return (
        <Affix offsetBottom={0}>
            <div style={{ background: '#fff', borderTop: '1px solid #f0f0f0', padding: '16px' }}>
                <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                    <Space direction="vertical" style={{ width: '100%' }} size="small">
                        {/* Knowledge context selector - shown when expanded */}
                        {showKnowledgeContext && (
                            <SourceSelector
                                selectedSourceIds={selectedSourceIds}
                                onSelectionChange={setSelectedSourceIds}
                                showCard={true}
                                compact={true}
                                placeholder="Select documents to provide context for better responses"
                            />
                        )}

                        {/* Context summary - shown when sources are selected but panel is collapsed */}
                        {!showKnowledgeContext && getContextSummary()}

                        {/* Main input area */}
                        <div style={{ display: 'flex', gap: '8px', alignItems: 'flex-end' }}>
                            <div style={{ flex: 1 }}>
                                <TextArea
                                    value={message}
                                    onChange={(e) => setMessage(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    placeholder={placeholder}
                                    disabled={disabled || loading}
                                    autoSize={{ minRows: 1, maxRows: 4 }}
                                    style={{
                                        borderRadius: '8px',
                                        resize: 'none'
                                    }}
                                />
                            </div>

                            <Space direction="vertical" size="small">
                                <Tooltip title={showKnowledgeContext ? "Hide knowledge context" : "Add knowledge context"}>
                                    <Button
                                        type={selectedSourceIds.length > 0 ? "primary" : "default"}
                                        ghost={selectedSourceIds.length > 0}
                                        icon={showKnowledgeContext ? <UpOutlined /> : <BookOutlined />}
                                        onClick={toggleKnowledgeContext}
                                        disabled={disabled}
                                        size="small"
                                    >
                                        {selectedSourceIds.length > 0 && (
                                            <Badge
                                                count={selectedSourceIds.length}
                                                size="small"
                                                offset={[2, -2]}
                                                style={{ fontSize: '10px' }}
                                            />
                                        )}
                                    </Button>
                                </Tooltip>

                                <Tooltip title="Send message">
                                    <Button
                                        type="primary"
                                        icon={<SendOutlined />}
                                        onClick={handleSend}
                                        disabled={disabled || loading || !message.trim()}
                                        loading={loading}
                                        size="large"
                                        style={{ borderRadius: '8px' }}
                                    >
                                        Send
                                    </Button>
                                </Tooltip>
                            </Space>
                        </div>

                        {/* Hint text */}
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Text type="secondary" style={{ fontSize: '11px' }}>
                                Press Shift+Enter for new line, Enter to send
                            </Text>

                            {selectedSourceIds.length === 0 && (
                                <Button
                                    type="link"
                                    size="small"
                                    onClick={toggleKnowledgeContext}
                                    style={{ fontSize: '11px', padding: 0 }}
                                >
                                    + Add knowledge context
                                </Button>
                            )}
                        </div>
                    </Space>
                </div>
            </div>
        </Affix>
    );
};

export default ChatInput;
