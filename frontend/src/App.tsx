import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider, theme } from 'antd';
import { NotificationProvider } from './contexts/NotificationContext';
import MainChatInterface from './components/chat/MainChatInterface';
import StatusBar from './components/layout/StatusBar';
import './App.css';

const App: React.FC = () => {
    return (
        <ConfigProvider
            theme={{
                algorithm: theme.defaultAlgorithm,
                token: {
                    colorPrimary: '#6366f1',
                    borderRadius: 8,
                    fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, sans-serif',
                },
            }}
        >
            <NotificationProvider>
                <Router>
                    <div className="app-container">
                        <StatusBar />
                        <Routes>
                            <Route path="/" element={<MainChatInterface />} />
                            <Route path="/chat" element={<MainChatInterface />} />
                            <Route path="*" element={<MainChatInterface />} />
                        </Routes>
                    </div>
                </Router>
            </NotificationProvider>
        </ConfigProvider>
    );
};

export default App;
