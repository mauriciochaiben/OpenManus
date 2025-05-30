import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout, ConfigProvider, theme } from 'antd';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';

import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import HomePage from './pages/HomePage';
import TaskDetailPage from './pages/TaskDetailPage';
import SettingsPage from './pages/SettingsPage';
import MCPConfigPage from './pages/MCPConfigPage';

import './App.css';

const { Content } = Layout;

// Create a client
const queryClient = new QueryClient({
    defaultOptions: {
        queries: {
            retry: 3,
            staleTime: 1000 * 60 * 5, // 5 minutes
        },
    },
});

const App: React.FC = () => {
    return (
        <QueryClientProvider client={queryClient}>
            <ConfigProvider
                theme={{
                    algorithm: theme.defaultAlgorithm,
                    token: {
                        colorPrimary: '#1890ff',
                        borderRadius: 8,
                        colorBgContainer: '#ffffff',
                    },
                }}
            >
                <Router>
                    <Layout className="app-layout">
                        <Sidebar />
                        <Layout className="main-layout">
                            <Header />
                            <Content className="main-content">
                                <Routes>
                                    <Route path="/" element={<HomePage />} />
                                    <Route path="/task/:id" element={<TaskDetailPage />} />
                                    <Route path="/settings" element={<SettingsPage />} />
                                    <Route path="/mcp-config" element={<MCPConfigPage />} />
                                </Routes>
                            </Content>
                        </Layout>
                    </Layout>
                </Router>
            </ConfigProvider>
            <ReactQueryDevtools initialIsOpen={false} />
        </QueryClientProvider>
    );
};

export default App;
