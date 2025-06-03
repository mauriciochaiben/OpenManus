import React, { useState, useRef, useEffect } from "react";
import {
  Card,
  Input,
  Button,
  Space,
  Typography,
  Tag,
  message,
  Empty,
  Spin,
  Tooltip,
  List,
  Avatar,
} from "antd";
import {
  SendOutlined,
  ClearOutlined,
  BulbOutlined,
  UserOutlined,
  RobotOutlined,
} from "@ant-design/icons";
import { chatApi } from "../services/api";
import type { ChatMessage } from "../types";

const { TextArea } = Input;
const { Text, Title } = Typography;

/**
 * Chat page component - uses chat feature components
 * Lazily loaded for better performance
 */
const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Load chat history on component mount
  useEffect(() => {
    loadChatHistory();
  }, []);

  const loadChatHistory = async () => {
    try {
      const history = await chatApi.getHistory();
      if (history.length === 0) {
        // Add welcome message if no history
        setMessages([
          {
            id: "1",
            role: "assistant",
            content:
              "Olá! Sou o OpenManus, seu assistente de IA. Posso ajudá-lo a processar documentos, analisar dados e executar tarefas complexas. Como posso ajudá-lo hoje?",
            timestamp: new Date().toISOString(),
          },
        ]);
      } else {
        setMessages(history);
      }
    } catch (error) {
      console.error("Error loading chat history:", error);
      // Add welcome message if error
      setMessages([
        {
          id: "1",
          role: "assistant",
          content:
            "Olá! Sou o OpenManus, seu assistente de IA. Posso ajudá-lo a processar documentos, analisar dados e executar tarefas complexas. Como posso ajudá-lo hoje?",
          timestamp: new Date().toISOString(),
        },
      ]);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage = inputValue.trim();
    setInputValue("");
    setIsLoading(true);

    try {
      const response = await chatApi.sendMessage({
        message: userMessage,
        context: {},
      });

      // Reload chat history to get the latest messages
      await loadChatHistory();

      // Set suggestions from response
      if (response.suggestions) {
        setSuggestions(response.suggestions);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      message.error("Erro ao enviar mensagem. Tente novamente.");
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
      setMessages([
        {
          id: "1",
          role: "assistant",
          content:
            "Olá! Sou o OpenManus, seu assistente de IA. Posso ajudá-lo a processar documentos, analisar dados e executar tarefas complexas. Como posso ajudá-lo hoje?",
          timestamp: new Date().toISOString(),
        },
      ]);
      setSuggestions([]);
      message.success("Histórico de chat limpo!");
    } catch (error) {
      console.error("Error clearing chat:", error);
      message.error("Erro ao limpar chat.");
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString("pt-BR", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div style={{ height: "100vh", display: "flex", flexDirection: "column" }}>
      <Card
        title={
          <Space>
            <RobotOutlined />
            <Title level={4} style={{ margin: 0 }}>
              AI Chat - OpenManus
            </Title>
          </Space>
        }
        extra={
          <Tooltip title="Limpar conversa">
            <Button
              icon={<ClearOutlined />}
              onClick={handleClearChat}
              type="text"
            />
          </Tooltip>
        }
        style={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          margin: 0,
          height: "100%",
        }}
        bodyStyle={{
          flex: 1,
          display: "flex",
          flexDirection: "column",
          padding: "16px",
          overflow: "hidden",
        }}
      >
        {/* Messages Area */}
        <div
          style={{
            flex: 1,
            overflowY: "auto",
            marginBottom: "16px",
            paddingRight: "8px",
          }}
        >
          {messages.length === 0 ? (
            <Empty
              description="Nenhuma mensagem ainda"
              style={{ marginTop: "20%" }}
            />
          ) : (
            <List
              dataSource={messages}
              renderItem={(msg) => {
                const isUser = msg.role === "user";
                return (
                  <List.Item
                    style={{
                      border: "none",
                      padding: "8px 0",
                      justifyContent: isUser ? "flex-end" : "flex-start",
                    }}
                  >
                    <div
                      style={{
                        maxWidth: "80%",
                        display: "flex",
                        alignItems: "flex-start",
                        flexDirection: isUser ? "row-reverse" : "row",
                      }}
                    >
                      <Avatar
                        icon={isUser ? <UserOutlined /> : <RobotOutlined />}
                        style={{
                          backgroundColor: isUser ? "#1890ff" : "#52c41a",
                          marginLeft: isUser ? "8px" : "0",
                          marginRight: isUser ? "0" : "8px",
                        }}
                      />
                      <div
                        style={{
                          background: isUser ? "#1890ff" : "#f6f6f6",
                          color: isUser ? "white" : "black",
                          padding: "12px 16px",
                          borderRadius: "12px",
                          borderTopLeftRadius: isUser ? "12px" : "4px",
                          borderTopRightRadius: isUser ? "4px" : "12px",
                        }}
                      >
                        <Text
                          style={{
                            color: isUser ? "white" : "inherit",
                            whiteSpace: "pre-wrap",
                          }}
                        >
                          {msg.content}
                        </Text>
                        <div
                          style={{
                            marginTop: "4px",
                            fontSize: "12px",
                            opacity: 0.7,
                          }}
                        >
                          {formatTime(msg.timestamp)}
                        </div>
                      </div>
                    </div>
                  </List.Item>
                );
              }}
            />
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggestions */}
        {suggestions.length > 0 && (
          <div style={{ marginBottom: "16px" }}>
            <Space size={[8, 8]} wrap>
              <BulbOutlined style={{ color: "#faad14" }} />
              <Text type="secondary">Sugestões:</Text>
              {suggestions.map((suggestion, index) => (
                <Tag
                  key={index}
                  color="blue"
                  style={{ cursor: "pointer" }}
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  {suggestion}
                </Tag>
              ))}
            </Space>
          </div>
        )}

        {/* Input Area */}
        <div style={{ display: "flex", gap: "8px" }}>
          <TextArea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Digite sua mensagem... (Enter para enviar, Shift+Enter para nova linha)"
            autoSize={{ minRows: 1, maxRows: 4 }}
            style={{ flex: 1 }}
            disabled={isLoading}
          />
          <Button
            type="primary"
            icon={isLoading ? <Spin size="small" /> : <SendOutlined />}
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
            style={{ alignSelf: "flex-end" }}
          >
            {isLoading ? "Enviando..." : "Enviar"}
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default ChatPage;
