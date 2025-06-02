import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { Layout } from 'antd';
import { NotificationProvider } from './contexts/NotificationContext';
import { Sidebar, Header, StatusBar } from './components/common';
import LazyLoadIndicator from './components/common/LazyLoadIndicator';
import AppRoutes from './routes';

const { Content } = Layout;

const AppRouter: React.FC = () => {
    return (
        <NotificationProvider>
            <Router>
                <LazyLoadIndicator />
                <Layout style={{ minHeight: '100vh' }}>
                    <Sidebar />
                    <Layout style={{ marginLeft: 250 }}>
                        <Header />
                        <StatusBar />
                        <Content style={{
                            padding: '32px',
                            background: '#f5f5f5',
                            minHeight: 'calc(100vh - 64px - 32px)',
                            overflow: 'auto'
                        }}>
                            <AppRoutes />
                        </Content>
                    </Layout>
                </Layout>
            </Router>
        </NotificationProvider>
    );
};

export default AppRouter;
