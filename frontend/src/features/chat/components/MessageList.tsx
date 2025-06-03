import React from "react";
import {
  List,
  Empty,
  Spin,
  Space,
  Typography,
  Avatar,
  Card,
  Button,
  Dropdown,
  message as antMessage,
  Tooltip,
  type MenuProps,
} from "antd";
import {
  MessageOutlined,
  UserOutlined,
  RobotOutlined,
  CopyOutlined,
  SaveOutlined,
  MoreOutlined,
} from "@ant-design/icons";
import type { ChatMessage } from "../../../types";
import { copyToClipboard, saveMessageAsNote } from "../utils/messageActions";
import "./MessageList.css";

const { Text, Paragraph } = Typography;

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
  const handleCopyText = async (content: string) => {
    try {
      await copyToClipboard(content);
      antMessage.success("Texto copiado para a área de transferência!");
    } catch (error) {
      antMessage.error("Falha ao copiar o texto");
    }
  };

  const handleSaveAsNote = async (msg: ChatMessage) => {
    try {
      await saveMessageAsNote(msg);
      antMessage.success("Mensagem salva como nota!");
    } catch (error) {
      antMessage.error("Falha ao salvar mensagem como nota");
    }
  };

  const getActionMenu = (msg: ChatMessage): MenuProps["items"] => [
    {
      key: "copy",
      label: "Copiar Texto",
      icon: <CopyOutlined />,
      onClick: () => handleCopyText(msg.content),
    },
    {
      key: "save",
      label: "Salvar como Nota",
      icon: <SaveOutlined />,
      onClick: () => handleSaveAsNote(msg),
    },
  ];

  const renderMessage = (msg: ChatMessage) => {
    const isUser = msg.role === "user";
    const actionMenu = getActionMenu(msg);

    return (
      <List.Item
        key={msg.id}
        className={`message-item ${
          isUser ? "user-message" : "assistant-message"
        }`}
        style={{
          border: "none",
          padding: "12px 0",
          justifyContent: isUser ? "flex-end" : "flex-start",
        }}
      >
        <div
          className={`message-container ${
            isUser ? "user-container" : "assistant-container"
          }`}
        >
          {/* Avatar */}
          <Avatar
            size={40}
            icon={isUser ? <UserOutlined /> : <RobotOutlined />}
            className={`message-avatar ${
              isUser ? "user-avatar" : "assistant-avatar"
            }`}
            style={{
              backgroundColor: isUser ? "#667eea" : "#10b981",
              flexShrink: 0,
              order: isUser ? 2 : 1,
            }}
          />

          {/* Message Content */}
          <Card
            className={`message-card ${
              isUser ? "user-card" : "assistant-card"
            }`}
            size="small"
            bordered={false}
            style={{
              maxWidth: "75%",
              margin: isUser ? "0 12px 0 auto" : "0 auto 0 12px",
              order: isUser ? 1 : 2,
              background: isUser
                ? "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
                : "#ffffff",
              borderRadius: "16px",
              borderTopRightRadius: isUser ? "6px" : "16px",
              borderTopLeftRadius: isUser ? "16px" : "6px",
              boxShadow: "0 2px 12px rgba(0, 0, 0, 0.08)",
              transition: "all 0.2s ease",
            }}
            bodyStyle={{ padding: "12px 16px" }}
          >
            {/* Message Text */}
            <Paragraph
              style={{
                margin: "0 0 8px 0",
                color: isUser ? "#ffffff" : "#333333",
                fontWeight: isUser ? 500 : 400,
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
                lineHeight: 1.6,
              }}
            >
              {msg.content}
            </Paragraph>

            {/* Footer with timestamp and actions */}
            <div
              className="message-footer"
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginTop: "8px",
              }}
            >
              <Text
                type="secondary"
                style={{
                  fontSize: "12px",
                  color: isUser ? "rgba(255, 255, 255, 0.8)" : "#999999",
                }}
              >
                {formatTime(msg.timestamp)}
              </Text>

              {/* Action buttons for assistant messages */}
              {!isUser && (
                <div
                  className="message-actions"
                  style={{
                    opacity: 0,
                    transition: "opacity 0.2s ease",
                  }}
                >
                  <Space size={4}>
                    <Tooltip title="Copiar Texto">
                      <Button
                        type="text"
                        size="small"
                        icon={<CopyOutlined />}
                        onClick={() => handleCopyText(msg.content)}
                        style={{
                          border: "none",
                          background: "transparent",
                          color: "#666666",
                          padding: "4px 6px",
                          height: "auto",
                          minWidth: "auto",
                        }}
                      />
                    </Tooltip>

                    <Tooltip title="Salvar como Nota">
                      <Button
                        type="text"
                        size="small"
                        icon={<SaveOutlined />}
                        onClick={() => handleSaveAsNote(msg)}
                        style={{
                          border: "none",
                          background: "transparent",
                          color: "#666666",
                          padding: "4px 6px",
                          height: "auto",
                          minWidth: "auto",
                        }}
                      />
                    </Tooltip>

                    <Dropdown
                      menu={{ items: actionMenu }}
                      trigger={["click"]}
                      placement="topRight"
                    >
                      <Tooltip title="Mais Ações">
                        <Button
                          type="text"
                          size="small"
                          icon={<MoreOutlined />}
                          style={{
                            border: "none",
                            background: "transparent",
                            color: "#666666",
                            padding: "4px 6px",
                            height: "auto",
                            minWidth: "auto",
                          }}
                        />
                      </Tooltip>
                    </Dropdown>
                  </Space>
                </div>
              )}
            </div>
          </Card>
        </div>
      </List.Item>
    );
  };

  // Loading state
  if (isLoading && messages.length === 0) {
    return (
      <div
        className="message-list"
        style={{ textAlign: "center", padding: "60px 20px" }}
      >
        <Spin size="large" />
        <div style={{ marginTop: "16px" }}>
          <Text type="secondary">Carregando conversa...</Text>
        </div>
      </div>
    );
  }

  // Empty state
  if (!isLoading && messages.length === 0) {
    return (
      <div className="message-list">
        <Empty
          image={
            <MessageOutlined style={{ fontSize: "64px", color: "#d9d9d9" }} />
          }
          description={
            <Space direction="vertical">
              <Text strong>Nenhuma mensagem ainda</Text>
              <Text type="secondary">
                Comece uma conversa digitando uma mensagem abaixo
              </Text>
            </Space>
          }
          style={{ padding: "60px 20px" }}
        />
      </div>
    );
  }

  return (
    <div className="message-list-wrapper">
      <List
        className="message-list"
        dataSource={messages}
        renderItem={renderMessage}
        loading={isLoading && messages.length > 0}
        locale={{
          emptyText: "Nenhuma mensagem encontrada",
        }}
        style={{
          padding: "0 16px",
          height: "100%",
          overflowY: "auto",
        }}
      />
    </div>
  );
};

export default MessageList;
