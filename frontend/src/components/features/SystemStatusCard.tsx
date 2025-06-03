import React, { useState, useEffect } from "react";
import { Card, Space, Tag, Button, Typography, List, Alert } from "antd";
import {
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  WifiOutlined,
  CloudServerOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { webSocketManager } from "../../services/websocket";
import { eventBus } from "../../utils/eventBus";
import { taskApi } from "../../services/api";

const { Text } = Typography;

interface ConnectionStatus {
  api: "connected" | "disconnected" | "checking";
  websocket: "connected" | "disconnected" | "checking";
  backend: "connected" | "disconnected" | "checking";
}

const SystemStatusCard: React.FC = () => {
  const [status, setStatus] = useState<ConnectionStatus>({
    api: "checking",
    websocket: "checking",
    backend: "checking",
  });
  const [lastCheck, setLastCheck] = useState<Date>(new Date());

  const checkApiConnection = async () => {
    try {
      await taskApi.getTasks();
      setStatus((prev) => ({ ...prev, api: "connected" }));
      return true;
    } catch (error) {
      setStatus((prev) => ({ ...prev, api: "disconnected" }));
      return false;
    }
  };

  const checkWebSocketConnection = () => {
    try {
      const connectionState = webSocketManager.getConnectionState();
      if (connectionState === "connected") {
        setStatus((prev) => ({ ...prev, websocket: "connected" }));
        return true;
      } else {
        setStatus((prev) => ({ ...prev, websocket: "disconnected" }));
        return false;
      }
    } catch (error) {
      setStatus((prev) => ({ ...prev, websocket: "disconnected" }));
      return false;
    }
  };

  const checkBackendHealth = async () => {
    try {
      // Assuming there's a health check endpoint
      const response = await fetch("http://localhost:8000/health");
      if (response.ok) {
        setStatus((prev) => ({ ...prev, backend: "connected" }));
        return true;
      } else {
        setStatus((prev) => ({ ...prev, backend: "disconnected" }));
        return false;
      }
    } catch (error) {
      setStatus((prev) => ({ ...prev, backend: "disconnected" }));
      return false;
    }
  };

  const runAllChecks = async () => {
    setStatus({
      api: "checking",
      websocket: "checking",
      backend: "checking",
    });

    await Promise.all([
      checkApiConnection(),
      checkWebSocketConnection(),
      checkBackendHealth(),
    ]);

    setLastCheck(new Date());
  };

  useEffect(() => {
    runAllChecks();

    // Check every 30 seconds
    const interval = setInterval(runAllChecks, 30000);

    // Listen for WebSocket connection state changes
    const unsubConnected = eventBus.on("websocket:connected", () => {
      setStatus((prev) => ({ ...prev, websocket: "connected" }));
    });

    const unsubDisconnected = eventBus.on("websocket:disconnected", () => {
      setStatus((prev) => ({ ...prev, websocket: "disconnected" }));
    });

    const unsubReconnecting = eventBus.on("websocket:reconnecting", () => {
      setStatus((prev) => ({ ...prev, websocket: "checking" }));
    });

    return () => {
      clearInterval(interval);
      unsubConnected();
      unsubDisconnected();
      unsubReconnecting();
    };
  }, []);

  const getStatusIcon = (connectionStatus: string) => {
    switch (connectionStatus) {
      case "connected":
        return <CheckCircleOutlined style={{ color: "#52c41a" }} />;
      case "disconnected":
        return <ExclamationCircleOutlined style={{ color: "#ff4d4f" }} />;
      default:
        return <ReloadOutlined spin style={{ color: "#faad14" }} />;
    }
  };

  const getStatusColor = (connectionStatus: string) => {
    switch (connectionStatus) {
      case "connected":
        return "success";
      case "disconnected":
        return "error";
      default:
        return "processing";
    }
  };

  const allConnected = Object.values(status).every((s) => s === "connected");
  const anyDisconnected = Object.values(status).some(
    (s) => s === "disconnected",
  );

  return (
    <Card
      title={
        <Space>
          <CloudServerOutlined />
          <span>System Status</span>
          {allConnected && <Tag color="success">All Systems Online</Tag>}
          {anyDisconnected && <Tag color="error">Connection Issues</Tag>}
        </Space>
      }
      extra={
        <Button
          size="small"
          icon={<ReloadOutlined />}
          onClick={runAllChecks}
          loading={Object.values(status).some((s) => s === "checking")}
        >
          Refresh
        </Button>
      }
      size="small"
    >
      <Space direction="vertical" style={{ width: "100%" }}>
        {anyDisconnected && (
          <Alert
            message="Connection Issues Detected"
            description="Some services are not responding. Check if the OpenManus backend is running."
            type="warning"
            showIcon
            closable
          />
        )}

        <List size="small">
          <List.Item>
            <Space>
              <WifiOutlined />
              <Text>Backend Server:</Text>
              <Tag
                color={getStatusColor(status.backend)}
                icon={getStatusIcon(status.backend)}
              >
                {status.backend.toUpperCase()}
              </Tag>
            </Space>
          </List.Item>

          <List.Item>
            <Space>
              <CloudServerOutlined />
              <Text>REST API:</Text>
              <Tag
                color={getStatusColor(status.api)}
                icon={getStatusIcon(status.api)}
              >
                {status.api.toUpperCase()}
              </Tag>
            </Space>
          </List.Item>

          <List.Item>
            <Space>
              <WifiOutlined />
              <Text>WebSocket:</Text>
              <Tag
                color={getStatusColor(status.websocket)}
                icon={getStatusIcon(status.websocket)}
              >
                {status.websocket.toUpperCase()}
              </Tag>
            </Space>
          </List.Item>
        </List>

        <Text type="secondary" style={{ fontSize: "12px" }}>
          Last checked: {lastCheck.toLocaleTimeString()}
        </Text>
      </Space>
    </Card>
  );
};

export default SystemStatusCard;
