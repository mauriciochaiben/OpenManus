import React from 'react'
import ReactDOM from 'react-dom/client'
import { ConfigProvider } from 'antd'
import ptBR from 'antd/locale/pt_BR'
import dayjs from 'dayjs'
import 'dayjs/locale/pt-br'
import App from './App.tsx'
import './index.css'
import { WebSocketService } from './services/websocket'

// Configure dayjs locale
dayjs.locale('pt-br')

// Initialize WebSocket service
WebSocketService.getInstance();

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
    </React.StrictMode>,
)
