import { lazy } from 'react';

// Core pages - carregamento prioritário
export const HomePage = lazy(() => import('../pages/HomePage'));
export const DashboardPage = lazy(() => import('../pages/DashboardPage'));

// Feature pages - carregamento sob demanda
export const ChatPage = lazy(() => import('../pages/ChatPage'));
export const KnowledgePage = lazy(() => import('../pages/Knowledge'));
export const TaskDetailPage = lazy(() => import('../pages/TaskDetailPage'));

// Configuration pages - carregamento diferido
export const LLMConfigurationPage = lazy(
  () => import('../features/llm-config/components/LLMConfigurationPage')
);
export const MCPConfigPage = lazy(() => import('../pages/MCPConfigPage'));
export const SettingsPage = lazy(() => import('../pages/SettingsPage'));
export const ThemeDemoPage = lazy(() => import('../pages/ThemeDemoPage'));

// Specialized apps - carregamento sob demanda
export const WorkflowApp = lazy(() => import('../WorkflowApp'));
