import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import { NotificationProvider } from './contexts/NotificationContext';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';
import StatusBar from './components/layout/StatusBar';

// Import all pages
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import ChatPage from './pages/ChatPage';
import Knowledge from './pages/Knowledge';
import LLMConfigurationPage from './features/llm-config/components/LLMConfigurationPage';
import MCPConfigPage from './pages/MCPConfigPage';
import SettingsPage from './pages/SettingsPage';
import TaskDetailPage from './pages/TaskDetailPage';

// Import the original workflow app for specific routes if needed
import WorkflowApp from './WorkflowApp';

const { Content } = Layout;

const AppRouter: React.FC = () => {
    return (
        <NotificationProvider>
            <Router>
                <Layout style={{ minHeight: '100vh' }}>
                    <Sidebar />
                    <Layout style={{ marginLeft: 250 }}>
                        <Header />
                        <StatusBar />
                        <Content style={{
                            padding: '24px',
                            background: '#f5f5f5',
                            minHeight: 'calc(100vh - 64px - 32px)'
                        }}>
                            <Routes>
                                <Route path="/" element={<HomePage />} />
                                <Route path="/dashboard" element={<DashboardPage />} />
                                <Route path="/chat" element={<ChatPage />} />
                                <Route path="/knowledge" element={<Knowledge />} />
                                <Route path="/llm-config" element={<LLMConfigurationPage />} />
                                <Route path="/mcp-config" element={<MCPConfigPage />} />
                                <Route path="/settings" element={<SettingsPage />} />
                                <Route path="/task/:id" element={<TaskDetailPage />} />
                                <Route path="/workflow" element={<WorkflowApp />} />
                            </Routes>
                        </Content>
                    </Layout>
                </Layout>
            </Router>
        </NotificationProvider>
    );
};

export default AppRouter;
