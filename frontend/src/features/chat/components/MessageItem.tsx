import React from 'react';
import {
    Avatar,
    Typography,
    Button,
    Space,
    Card,
    Dropdown,
    message
} from 'antd';
import {
    UserOutlined,
    RobotOutlined,
    CopyOutlined,
    SaveOutlined,
    MoreOutlined
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import type { ChatMessage } from '../../../types';
import { copyToClipboard, saveMessageAsNote } from '../utils/messageActions';

const { Text } = Typography;

interface MessageItemProps {
    message: ChatMessage;
    formatTime: (timestamp: string) => string;
}

const MessageItem: React.FC<MessageItemProps> = ({ message: msg, formatTime }) => {
    const isUser = msg.role === 'user';

    const handleCopyText = async (content: string) => {
        try {
            await copyToClipboard(content);
            message.success('Message copied to clipboard!');
        } catch (error) {
            message.error('Failed to copy message');
        }
    };

    const handleSaveAsNote = async (msg: ChatMessage) => {
        try {
            await saveMessageAsNote(msg);
            message.success('Message saved as note!');
        } catch (error) {
            message.error('Failed to save message as note');
        }
    };

    const getMessageActions = (): MenuProps['items'] => {
        if (isUser) return [];

        return [
            {
                key: 'copy',
                label: 'Copy Text',
                icon: <CopyOutlined />,
                onClick: () => handleCopyText(msg.content)
            },
            {
                key: 'save',
                label: 'Save as Note',
                icon: <SaveOutlined />,
                onClick: () => handleSaveAsNote(msg)
            }
        ];
    };

    const actions = getMessageActions();

    return (
        <div className={`message-wrapper ${isUser ? 'user-wrapper' : 'assistant-wrapper'}`}>
            {/* Avatar */}
            <Avatar
                className={`message-avatar ${isUser ? 'user-avatar' : 'assistant-avatar'}`}
                icon={isUser ? <UserOutlined /> : <RobotOutlined />}
                size={40}
            />

            {/* Message Content */}
            <Card
                className={`message-card ${isUser ? 'user-card' : 'assistant-card'}`}
                size="small"
                bordered={false}
            >
                <div className="message-content">
                    <div className="message-text">
                        <Text className={isUser ? 'user-text' : 'assistant-text'}>
                            {msg.content}
                        </Text>
                    </div>

                    <div className="message-footer">
                        <div className="message-timestamp">
                            <Text type="secondary" className="timestamp-text">
                                {formatTime(msg.timestamp)}
                            </Text>
                        </div>

                        {/* Action buttons for assistant messages */}
                        {!isUser && actions && actions.length > 0 && (
                            <div className="message-actions">
                                <Space size="small">
                                    <Button
                                        type="text"
                                        size="small"
                                        icon={<CopyOutlined />}
                                        onClick={() => handleCopyText(msg.content)}
                                        className="action-button"
                                        title="Copy Text"
                                    />
                                    <Button
                                        type="text"
                                        size="small"
                                        icon={<SaveOutlined />}
                                        onClick={() => handleSaveAsNote(msg)}
                                        className="action-button"
                                        title="Save as Note"
                                    />
                                    <Dropdown
                                        menu={{ items: actions }}
                                        trigger={['click']}
                                        placement="topRight"
                                    >
                                        <Button
                                            type="text"
                                            size="small"
                                            icon={<MoreOutlined />}
                                            className="action-button"
                                            title="More Actions"
                                        />
                                    </Dropdown>
                                </Space>
                            </div>
                        )}
                    </div>
                </div>
            </Card>
        </div>
    );
};

export default MessageItem;
