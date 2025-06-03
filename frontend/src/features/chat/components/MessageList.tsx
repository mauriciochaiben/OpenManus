import React from 'react';
import { List, Empty, Spin, Space, Typography } from 'antd';
import { MessageOutlined } from '@ant-design/icons';
import type { ChatMessage } from '../../../types';
import MessageItem from './MessageItem';
import './MessageList.css';

const { Text } = Typography;

interface MessageListProps {
  messages: ChatMessage[];
  isLoading?: boolean;
  formatTime: (timestamp: string) => string;
}

const MessageList: React.FC<MessageListProps> = ({
  messages,
  isLoading = false,
  formatTime,
}) => {
  const renderMessage = (msg: ChatMessage) => (
    <List.Item
      key={msg.id}
      className={`message-item ${
        msg.role === 'user' ? 'user-message' : 'assistant-message'
      }`}
    >
      <MessageItem message={msg} formatTime={formatTime} />
    </List.Item>
  );

  // Loading state
  if (isLoading && messages.length === 0) {
    return (
      <div
        className='message-list'
        style={{ textAlign: 'center', padding: '60px 20px' }}
      >
        <Spin size='large' />
        <div style={{ marginTop: '16px' }}>
          <Text type='secondary'>Carregando conversa...</Text>
        </div>
      </div>
    );
  }

  // Empty state
  if (!isLoading && messages.length === 0) {
    return (
      <div className='message-list'>
        <Empty
          image={
            <MessageOutlined style={{ fontSize: '64px', color: '#d9d9d9' }} />
          }
          description={
            <Space direction='vertical'>
              <Text strong>Nenhuma mensagem ainda</Text>
              <Text type='secondary'>
                Comece uma conversa digitando uma mensagem abaixo
              </Text>
            </Space>
          }
          style={{ padding: '60px 20px' }}
        />
      </div>
    );
  }

  return (
    <List
      className='message-list'
      dataSource={messages}
      renderItem={renderMessage}
      loading={isLoading && messages.length > 0} // Show loading only when adding to existing messages
      locale={{
        emptyText: 'Nenhuma mensagem encontrada',
      }}
    />
  );
};

export default MessageList;
