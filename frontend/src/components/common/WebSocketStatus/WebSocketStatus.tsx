// WebSocket status indicator component
import React from 'react';
import { useWebSocket } from '../../../hooks/useWebSocket';
import './WebSocketStatus.css';

const WebSocketStatus: React.FC = () => {
  const { connectionState, isConnected, connect, disconnect } = useWebSocket();

  const getStatusInfo = () => {
    switch (connectionState) {
      case 'connected':
        return {
          icon: '🟢',
          text: 'Connected',
          className: 'ws-status--connected',
        };
      case 'connecting':
        return {
          icon: '🟡',
          text: 'Connecting...',
          className: 'ws-status--connecting',
        };
      case 'reconnecting':
        return {
          icon: '🟠',
          text: 'Reconnecting...',
          className: 'ws-status--reconnecting',
        };
      case 'failed':
        return {
          icon: '🔴',
          text: 'Connection failed',
          className: 'ws-status--failed',
        };
      case 'disconnected':
      default:
        return {
          icon: '⚫',
          text: 'Disconnected',
          className: 'ws-status--disconnected',
        };
    }
  };

  const statusInfo = getStatusInfo();

  const handleToggleConnection = () => {
    if (isConnected) {
      disconnect();
    } else {
      connect();
    }
  };

  return (
    <div className={`ws-status ${statusInfo.className}`}>
      <div className='ws-status__indicator'>
        <span className='ws-status__icon'>{statusInfo.icon}</span>
        <span className='ws-status__text'>{statusInfo.text}</span>
      </div>
      <button
        className='ws-status__toggle'
        onClick={handleToggleConnection}
        disabled={
          connectionState === 'connecting' || connectionState === 'reconnecting'
        }
        title={isConnected ? 'Disconnect WebSocket' : 'Connect WebSocket'}
      >
        {isConnected ? 'Disconnect' : 'Connect'}
      </button>
    </div>
  );
};

export default WebSocketStatus;
