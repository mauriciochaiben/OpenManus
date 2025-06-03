import React, { useState, useEffect } from 'react';
import { Badge, Space, Typography } from 'antd';
import {
  WifiOutlined,
  CloudServerOutlined,
  RobotOutlined,
  SettingOutlined,
  HistoryOutlined,
} from '@ant-design/icons';
import { webSocketManager } from '../../../services/websocket';
import { eventBus } from '../../../utils/eventBus';

const { Text } = Typography;

interface SystemStatus {
  websocket: 'connected' | 'disconnected' | 'connecting';
  backend: 'connected' | 'disconnected';
  activeAgents: number;
  tasksInProgress: number;
}

const StatusBar: React.FC = () => {
  const [status, setStatus] = useState<SystemStatus>({
    websocket: 'disconnected',
    backend: 'disconnected',
    activeAgents: 0,
    tasksInProgress: 0,
  });

  useEffect(() => {
    // Check initial WebSocket status
    const checkWebSocketStatus = () => {
      const connectionState = webSocketManager.getConnectionState();
      setStatus((prev) => ({
        ...prev,
        websocket:
          connectionState === 'connected'
            ? 'connected'
            : connectionState === 'connecting'
              ? 'connecting'
              : 'disconnected',
      }));
    };

    // Check backend health
    const checkBackendHealth = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) {
          setStatus((prev) => ({ ...prev, backend: 'connected' }));
        } else {
          setStatus((prev) => ({ ...prev, backend: 'disconnected' }));
        }
      } catch (error) {
        setStatus((prev) => ({ ...prev, backend: 'disconnected' }));
      }
    };

    // Initial checks
    checkWebSocketStatus();
    checkBackendHealth();

    // Set up periodic health checks
    const healthCheckInterval = setInterval(checkBackendHealth, 30000);

    // Listen to WebSocket events
    const unsubscribeConnected = eventBus.on('websocket:connected', () => {
      setStatus((prev) => ({ ...prev, websocket: 'connected' }));
    });

    const unsubscribeDisconnected = eventBus.on(
      'websocket:disconnected',
      () => {
        setStatus((prev) => ({ ...prev, websocket: 'disconnected' }));
      }
    );

    const unsubscribeTaskUpdate = eventBus.on('task:updated', (task: any) => {
      // Update task count if needed
      if (task.status === 'running') {
        setStatus((prev) => ({
          ...prev,
          tasksInProgress: prev.tasksInProgress + 1,
        }));
      } else if (task.status === 'completed' || task.status === 'failed') {
        setStatus((prev) => ({
          ...prev,
          tasksInProgress: Math.max(0, prev.tasksInProgress - 1),
        }));
      }
    });

    return () => {
      clearInterval(healthCheckInterval);
      unsubscribeConnected();
      unsubscribeDisconnected();
      unsubscribeTaskUpdate();
    };
  }, []);

  const getStatusColor = (
    statusType: 'connected' | 'disconnected' | 'connecting'
  ) => {
    switch (statusType) {
      case 'connected':
        return '#52c41a';
      case 'connecting':
        return '#faad14';
      case 'disconnected':
        return '#ff4d4f';
      default:
        return '#d9d9d9';
    }
  };

  const openSettings = () => {
    // Could open a settings modal or navigate to settings
    console.log('Settings clicked');
  };

  const openHistory = () => {
    // Could open chat history or task history
    console.log('History clicked');
  };

  return (
    <div className='status-bar'>
      <Space size='large'>
        <div className='status-item'>
          <Badge
            status={
              status.websocket === 'connected'
                ? 'success'
                : status.websocket === 'connecting'
                  ? 'processing'
                  : 'error'
            }
          />
          <WifiOutlined style={{ color: getStatusColor(status.websocket) }} />
          <Text style={{ color: getStatusColor(status.websocket) }}>
            WebSocket:{' '}
            {status.websocket === 'connected'
              ? 'Conectado'
              : status.websocket === 'connecting'
                ? 'Conectando'
                : 'Desconectado'}
          </Text>
        </div>

        <div className='status-item'>
          <Badge
            status={status.backend === 'connected' ? 'success' : 'error'}
          />
          <CloudServerOutlined
            style={{ color: getStatusColor(status.backend) }}
          />
          <Text style={{ color: getStatusColor(status.backend) }}>
            Backend:{' '}
            {status.backend === 'connected' ? 'Conectado' : 'Desconectado'}
          </Text>
        </div>

        <div className='status-item'>
          <RobotOutlined style={{ color: '#1890ff' }} />
          <Text>Agentes Ativos: {status.activeAgents}</Text>
        </div>

        {status.tasksInProgress > 0 && (
          <div className='status-item status-processing'>
            <Badge count={status.tasksInProgress} size='small' />
            <Text>Tarefas em Progresso</Text>
          </div>
        )}
      </Space>

      <Space>
        <div
          className='status-item'
          style={{ cursor: 'pointer' }}
          onClick={openHistory}
        >
          <HistoryOutlined />
          <Text>Histórico</Text>
        </div>

        <div
          className='status-item'
          style={{ cursor: 'pointer' }}
          onClick={openSettings}
        >
          <SettingOutlined />
          <Text>Configurações</Text>
        </div>
      </Space>
    </div>
  );
};

export default StatusBar;
