import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { NotificationProvider } from '../contexts/NotificationContext';
import { MainLayout } from '../layouts';
import LazyLoadIndicator from '../components/common/LazyLoadIndicator';
import AppRoutes from '../routes';

/**
 * AppRouter alternativo usando o MainLayout refatorado
 * Este componente demonstra como usar o novo MainLayout que integra
 * todos os componentes de layout (Sider, Header, Content) em um único lugar
 */
const AppRouterWithMainLayout: React.FC = () => {
    return (
        <NotificationProvider>
            <Router>
                <LazyLoadIndicator />
                <MainLayout>
                    <AppRoutes />
                </MainLayout>
            </Router>
        </NotificationProvider>
    );
};

export default AppRouterWithMainLayout;
