import React from 'react';
import { Routes } from 'react-router-dom';
import { CoreRoutes, FeatureRoutes, ConfigRoutes } from './routeGroups';

/**
 * Configuração principal de rotas com lazy loading
 * Organizada em grupos lógicos para melhor performance e manutenibilidade
 */
const AppRoutes: React.FC = () => {
    return (
        <Routes>
            {/* Rotas principais - carregamento prioritário */}
            {CoreRoutes()}

            {/* Rotas de funcionalidades - carregamento sob demanda */}
            {FeatureRoutes()}

            {/* Rotas de configuração - carregamento diferido */}
            {ConfigRoutes()}
        </Routes>
    );
};

export default AppRoutes;
