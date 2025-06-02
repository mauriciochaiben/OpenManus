import React, { useState, useRef, useEffect } from 'react';
import {
    Input,
    Button,
    Space,
    Typography,
    Tag,
    message,
    Spin,
    Badge,
    Dropdown,
    Progress,
    type MenuProps
} from 'antd';
import {
    SendOutlined,
    RobotOutlined,
    ClearOutlined,
    BulbOutlined,
    SettingOutlined,
    HistoryOutlined,
    BranchesOutlined,
    ThunderboltOutlined,
    ApiOutlined,
    MoreOutlined
} from '@ant-design/icons';
import { chatApi } from '../../../services/api';
import { webSocketManager } from '../../../services/websocket';
import { eventBus } from '../../../utils/eventBus';
import type { ChatMessage } from '../../../types';
import { MessageList } from '../../../features/chat/components';

const { TextArea } = Input;
const { Text, Title } = Typography;

interface ProcessingStatus {
    type: 'single' | 'multi' | 'mcp' | null;
    stage: string;
    progress: number;
    agents?: string[];
}

const MainChatInterface: React.FC = () => {
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [suggestions, setSuggestions] = useState<string[]>([]);
    const [processingStatus, setProcessingStatus] = useState<ProcessingStatus>({ type: null, stage: '', progress: 0 });
    const [isWebSocketConnected, setIsWebSocketConnected] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Auto-scroll to bottom when messages change
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // Initialize WebSocket connection and load chat history
    useEffect(() => {
        loadChatHistory();
        initializeWebSocket();

        // Listen to WebSocket events
        const unsubscribeConnected = eventBus.on('websocket:connected', () => {
            setIsWebSocketConnected(true);
        });

        const unsubscribeDisconnected = eventBus.on('websocket:disconnected', () => {
            setIsWebSocketConnected(false);
        });

        const unsubscribeMessage = eventBus.on('websocket:message', (data: any) => {
            handleWebSocketMessage(data);
        });

        return () => {
            unsubscribeConnected();
            unsubscribeDisconnected();
            unsubscribeMessage();
        };
    }, []);

    const initializeWebSocket = () => {
        try {
            webSocketManager.connect();
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
        }
    };

    const handleWebSocketMessage = (data: any) => {
        if (data.type === 'chat_message') {
            // Real-time message received
            loadChatHistory(); // Refresh messages
        } else if (data.type === 'task_progress') {
            // Update processing status with detailed information
            const stage = data.stage || data.description || 'Processando...';
            const progress = data.progress || 0;
            const agents = data.agents || [];
            const execution_type = data.execution_type || null;

            // Create more descriptive stage message
            let detailedStage = stage;
            if (data.step_number && data.total_steps) {
                detailedStage = `Passo ${data.step_number}/${data.total_steps}: ${stage}`;
            } else if (data.task_name) {
                detailedStage = `${data.task_name} - ${stage}`;
            }

            setProcessingStatus({
                type: execution_type,
                stage: detailedStage,
                progress: Math.min(100, Math.max(0, progress)),
                agents: agents
            });
        } else if (data.type === 'task_completed') {
            // Clear processing status
            setProcessingStatus({ type: null, stage: '', progress: 0 });
            // Reload messages to show final result
            loadChatHistory();
        } else if (data.type === 'task_failed') {
            // Show error status
            setProcessingStatus({
                type: null,
                stage: 'Erro no processamento',
                progress: 0,
                agents: []
            });
            // Reload messages to show error
            setTimeout(() => {
                loadChatHistory();
                setProcessingStatus({ type: null, stage: '', progress: 0 });
            }, 2000);
        }
    };

    const loadChatHistory = async () => {
        try {
            const history = await chatApi.getHistory();
            if (history.length === 0) {
                // Add welcome message if no history
                setMessages([{
                    id: '1',
                    role: 'assistant',
                    content: 'Como posso ajudá-lo hoje? 💭',
                    timestamp: new Date().toISOString(),
                }]);
            } else {
                setMessages(history);
            }
        } catch (error) {
            console.error('Error loading chat history:', error);
            // Add welcome message if error
            setMessages([{
                id: '1',
                role: 'assistant',
                content: 'Como posso ajudá-lo hoje? 💭',
                timestamp: new Date().toISOString(),
            }]);
        }
    };

    const handleSendMessage = async () => {
        if (!inputValue.trim() || isLoading) return;

        const userMessage = inputValue.trim();
        setInputValue('');
        setIsLoading(true);

        // Initialize processing status - will be updated by WebSocket
        setProcessingStatus({
            type: null,
            stage: 'Iniciando processamento...',
            progress: 5
        });

        try {
            const response = await chatApi.sendMessage({
                message: userMessage,
                context: {}
            });

            // Reload chat history to get the latest messages
            await loadChatHistory();

            // Set suggestions from response
            if (response.suggestions) {
                setSuggestions(response.suggestions);
            }

            // Clear processing status
            setProcessingStatus({ type: null, stage: '', progress: 0 });

        } catch (error) {
            console.error('Error sending message:', error);
            message.error('Erro ao enviar mensagem. Tente novamente.');
            setProcessingStatus({ type: null, stage: '', progress: 0 });
        } finally {
            setIsLoading(false);
        }
    };

    const handleSuggestionClick = (suggestion: string) => {
        setInputValue(suggestion);
        setSuggestions([]);
    };

    const handleClearChat = async () => {
        try {
            await chatApi.clearHistory();
            setMessages([{
                id: '1',
                role: 'assistant',
                content: 'Como posso ajudá-lo hoje? 💭',
                timestamp: new Date().toISOString(),
            }]);
            setSuggestions([]);
            setProcessingStatus({ type: null, stage: '', progress: 0 });
            message.success('Histórico de chat limpo!');
        } catch (error) {
            console.error('Error clearing chat:', error);
            message.error('Erro ao limpar chat.');
        }
    };

    const handleKeyPress = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    const getExecutionTypeIcon = (type: string) => {
        switch (type) {
            case 'single': return <RobotOutlined />;
            case 'multi': return <BranchesOutlined />;
            case 'mcp': return <ApiOutlined />;
            default: return <ThunderboltOutlined />;
        }
    };

    const getExecutionTypeLabel = (type: string) => {
        switch (type) {
            case 'single': return 'Agente Único';
            case 'multi': return 'Multi-Agentes';
            case 'mcp': return 'Protocolo MCP';
            default: return 'Processando';
        }
    };

    const menuItems: MenuProps['items'] = [
        {
            key: 'history',
            label: 'Histórico Completo',
            icon: <HistoryOutlined />,
        },
        {
            key: 'settings',
            label: 'Configurações',
            icon: <SettingOutlined />,
        },
        {
            type: 'divider',
        },
        {
            key: 'clear',
            label: 'Limpar Conversa',
            icon: <ClearOutlined />,
            danger: true,
            onClick: handleClearChat,
        },
    ];

    return (
        <div className="main-chat-container">
            {/* Chat Header */}
            <div className="chat-header">
                <div className="chat-title">
                    <Space>
                        <div className="chat-logo">
                            <RobotOutlined />
                        </div>
                        <div>
                            <Title level={4} style={{ margin: 0, color: 'white' }}>
                                OpenManus AI
                            </Title>
                            <div className="connection-status">
                                <Badge
                                    status={isWebSocketConnected ? 'success' : 'error'}
                                    text={isWebSocketConnected ? 'Conectado' : 'Desconectado'}
                                />
                            </div>
                        </div>
                    </Space>
                </div>

                <div className="chat-actions">
                    <Dropdown menu={{ items: menuItems }} trigger={['click']}>
                        <Button
                            type="text"
                            icon={<MoreOutlined />}
                            style={{ color: 'white' }}
                        />
                    </Dropdown>
                </div>
            </div>

            {/* Processing Status */}
            {(isLoading || processingStatus.type) && (
                <div className="processing-status">
                    <Space direction="vertical" style={{ width: '100%' }}>
                        <Space>
                            {processingStatus.type && getExecutionTypeIcon(processingStatus.type)}
                            <Spin size="small" />
                            <Text strong>
                                {processingStatus.type
                                    ? `${getExecutionTypeLabel(processingStatus.type)} - ${processingStatus.stage}`
                                    : processingStatus.stage || 'Processando...'
                                }
                            </Text>
                        </Space>

                        {/* Progress Bar */}
                        {processingStatus.progress > 0 && (
                            <Progress
                                percent={processingStatus.progress}
                                size="small"
                                status="active"
                                showInfo={true}
                                format={(percent) => `${percent}%`}
                            />
                        )}

                        {/* Active Agents */}
                        {processingStatus.agents && processingStatus.agents.length > 0 && (
                            <div className="active-agents">
                                <Text type="secondary" style={{ marginRight: 8 }}>
                                    Agentes ativos:
                                </Text>
                                {processingStatus.agents.map(agent => (
                                    <Tag key={agent} color="blue" icon={<RobotOutlined />}>
                                        {agent}
                                    </Tag>
                                ))}
                            </div>
                        )}
                    </Space>
                </div>
            )}

            {/* Messages Area */}
            <div className="messages-container">
                <MessageList
                    messages={messages}
                    isLoading={isLoading}
                    formatTime={(timestamp: string) => {
                        return new Date(timestamp).toLocaleTimeString('pt-BR', {
                            hour: '2-digit',
                            minute: '2-digit'
                        });
                    }}
                />
                <div ref={messagesEndRef} />
            </div>

            {/* Suggestions */}
            {suggestions.length > 0 && (
                <div className="suggestions-container">
                    <Space size={[8, 8]} wrap>
                        <BulbOutlined className="suggestions-icon" />
                        <Text type="secondary">Sugestões:</Text>
                        {suggestions.map((suggestion, index) => (
                            <Tag
                                key={index}
                                className="suggestion-tag"
                                onClick={() => handleSuggestionClick(suggestion)}
                            >
                                {suggestion}
                            </Tag>
                        ))}
                    </Space>
                </div>
            )}

            {/* Input Area */}
            <div className="input-container">
                <div className="input-wrapper">
                    <TextArea
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyPress={handleKeyPress}
                        placeholder="Digite sua mensagem... (Enter para enviar, Shift+Enter para nova linha)"
                        autoSize={{ minRows: 1, maxRows: 4 }}
                        className="message-input"
                        disabled={isLoading}
                    />
                    <Button
                        type="primary"
                        icon={isLoading ? <Spin size="small" /> : <SendOutlined />}
                        onClick={handleSendMessage}
                        disabled={!inputValue.trim() || isLoading}
                        className="send-button"
                        size="large"
                    >
                        {isLoading ? 'Enviando...' : 'Enviar'}
                    </Button>
                </div>
            </div>
        </div>
    );
};

export default MainChatInterface;
