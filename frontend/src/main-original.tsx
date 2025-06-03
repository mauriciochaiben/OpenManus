import React from 'react';
import ReactDOM from 'react-dom/client';
import { ConfigProvider } from 'antd';
import ptBR from 'antd/locale/pt_BR';
import dayjs from 'dayjs';
import 'dayjs/locale/pt-br';
import App from './App.tsx';
import './index.css';
import { webSocketManager } from './services/websocket';

// Configure dayjs locale
dayjs.locale('pt-br');

// Initialize WebSocket service (optional connection)
try {
  // Generate a unique client ID for this session
  const clientId = `frontend-${Date.now()}-${Math.random()
    .toString(36)
    .substr(2, 9)}`;
  const baseWsUrl =
    import.meta.env.VITE_WS_URL || 'ws://localhost:8000/api/v2/chat/ws';
  const wsUrl = `${baseWsUrl}/${clientId}`;

  console.log('Initializing WebSocket with URL:', wsUrl);
  webSocketManager.initialize(wsUrl);
} catch (error) {
  console.warn('WebSocket service initialization failed:', error);
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ConfigProvider
      locale={ptBR}
      theme={{
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 8,
        },
      }}
    >
      <App />
    </ConfigProvider>
  </React.StrictMode>
);
