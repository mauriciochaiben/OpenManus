import React, { useState, useRef, useEffect } from 'react';
import {
  Card,
  Input,
  Button,
  Space,
  Typography,
  Tag,
  message,
  Spin,
  Layout,
} from 'antd';
import { SendOutlined, ClearOutlined, BulbOutlined } from '@ant-design/icons';
import { MessageList } from '../features/chat/components';
import { SourceSelector } from '../shared/components';
import { chatApi } from '../services/api';
import type { ChatMessage } from '../types';

const { TextArea } = Input;
const { Title } = Typography;
const { Content } = Layout;

/**
 * Chat page component - uses chat feature components
 * Lazily loaded for better performance
 */
const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedSourceIds, setSelectedSourceIds] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage({
        message: userMessage.content,
        context:
          selectedSourceIds.length > 0
            ? { knowledge_source_ids: selectedSourceIds }
            : {},
      });

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.message,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      message.error('Failed to send message. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([]);
    setInputValue('');
    setSelectedSourceIds([]);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Content style={{ padding: '24px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Title level={2}>AI Chat Assistant</Title>

        {/* Knowledge Source Selection */}
        <SourceSelector
          selectedSourceIds={selectedSourceIds}
          onSelectionChange={setSelectedSourceIds}
          compact={true}
        />

        {/* Chat Messages */}
        <Card
          style={{
            height: 'calc(100vh - 400px)',
            marginBottom: '16px',
            overflow: 'hidden',
          }}
          bodyStyle={{
            height: '100%',
            overflow: 'auto',
            padding: '16px',
          }}
        >
          <MessageList
            messages={messages}
            isLoading={isLoading}
            formatTime={formatTime}
          />
          <div ref={messagesEndRef} />
        </Card>

        {/* Message Input */}
        <Card>
          <Space.Compact style={{ width: '100%' }}>
            <TextArea
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder='Type your message... (Shift+Enter for new line)'
              autoSize={{ minRows: 1, maxRows: 4 }}
              disabled={isLoading}
              style={{ flex: 1 }}
            />
            <Space>
              <Button
                type='default'
                icon={<ClearOutlined />}
                onClick={handleClear}
                disabled={isLoading || messages.length === 0}
                title='Clear conversation'
              />
              <Button
                type='primary'
                icon={isLoading ? <Spin size='small' /> : <SendOutlined />}
                onClick={handleSend}
                disabled={!inputValue.trim() || isLoading}
                loading={isLoading}
              >
                Send
              </Button>
            </Space>
          </Space.Compact>

          {selectedSourceIds.length > 0 && (
            <div style={{ marginTop: '8px' }}>
              <Space>
                <BulbOutlined style={{ color: '#1890ff' }} />
                <Tag color='blue'>
                  {selectedSourceIds.length} knowledge source(s) selected
                </Tag>
              </Space>
            </div>
          )}
        </Card>
      </div>
    </Content>
  );
};

export default ChatPage;
