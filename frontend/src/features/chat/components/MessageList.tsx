import React from 'react';
import { List } from 'antd';
import type { ChatMessage } from '../../../types';
import MessageItem from './MessageItem';
import './MessageList.css';

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

  return (
    <List
      className='message-list'
      dataSource={messages}
      renderItem={renderMessage}
      loading={isLoading}
      locale={{
        emptyText: 'No messages yet. Start a conversation!',
      }}
    />
  );
};

export default MessageList;
