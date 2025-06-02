import React from 'react';
import { Route } from 'react-router-dom';
import LazyRouteWrapper from './components/LazyRouteWrapper';
import * as LazyComponents from './lazyComponents';

/**
 * Core application routes - páginas principais e essenciais
 */
export const CoreRoutes = () => (
    <>
        <Route
            path="/"
            element={
                <LazyRouteWrapper
                    loadingMessage="Carregando página inicial..."
                    componentName="HomePage"
                >
                    <LazyComponents.HomePage />
                </LazyRouteWrapper>
            }
        />
        <Route
            path="/dashboard"
            element={
                <LazyRouteWrapper
                    loadingMessage="Carregando painel..."
                    componentName="DashboardPage"
                >
                    <LazyComponents.DashboardPage />
                </LazyRouteWrapper>
            }
        />
    </>
);

/**
 * Feature routes - funcionalidades principais do sistema
 */
export const FeatureRoutes = () => (
    <>
        <Route
            path="/chat"
            element={
                <LazyRouteWrapper
                    loadingMessage="Carregando chat..."
                    componentName="ChatPage"
                >
                    <LazyComponents.ChatPage />
                </LazyRouteWrapper>
            }
        />
        <Route
            path="/knowledge"
            element={
                <LazyRouteWrapper
                    loadingMessage="Carregando base de conhecimento..."
                    componentName="KnowledgePage"
                >
                    <LazyComponents.KnowledgePage />
                </LazyRouteWrapper>
            }
        />
        <Route
            path="/task/:id"
            element={
                <LazyRouteWrapper loadingMessage="Carregando detalhes da tarefa...">
                    <LazyComponents.TaskDetailPage />
                </LazyRouteWrapper>
            }
        />
        <Route
            path="/workflow"
            element={
                <LazyRouteWrapper loadingMessage="Carregando workflow...">
                    <LazyComponents.WorkflowApp />
                </LazyRouteWrapper>
            }
        />
    </>
);

/**
 * Configuration routes - páginas de configuração e administração
 */
export const ConfigRoutes = () => (
    <>
        <Route
            path="/llm-config"
            element={
                <LazyRouteWrapper loadingMessage="Carregando configurações LLM...">
                    <LazyComponents.LLMConfigurationPage />
                </LazyRouteWrapper>
            }
        />
        <Route
            path="/mcp-config"
            element={
                <LazyRouteWrapper loadingMessage="Carregando configurações MCP...">
                    <LazyComponents.MCPConfigPage />
                </LazyRouteWrapper>
            }
        />
        <Route
            path="/settings"
            element={
                <LazyRouteWrapper loadingMessage="Carregando configurações...">
                    <LazyComponents.SettingsPage />
                </LazyRouteWrapper>
            }
        />
    </>
);
