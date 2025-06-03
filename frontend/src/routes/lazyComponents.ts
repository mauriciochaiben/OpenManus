import { lazy } from 'react';

// Core pages - carregamento prioritário
export const HomePage = lazy(() => import('../pages/HomePage'));
export const DashboardPage = lazy(() => import('../pages/DashboardPage'));

// Feature pages - carregamento sob demanda por domínio
// Communication & Interaction
export const ChatPage = lazy(() => import('../pages/ChatPage'));

// Knowledge Management
export const KnowledgePage = lazy(() => import('../pages/Knowledge'));

// Productivity & Organization
export const NotesPage = lazy(() => import('../pages/NotesPage'));
export const TasksPage = lazy(() => import('../pages/TasksPage'));
export const TaskDetailPage = lazy(() => import('../pages/TaskDetailPage'));

// Agents & Automation
export const AgentsPage = lazy(() => import('../pages/AgentsPage'));

// Visual & Creative
export const CanvasPage = lazy(() => import('../pages/CanvasPage'));

// Configuration pages - carregamento diferido
export const LLMConfigurationPage = lazy(
  () => import('../features/llm-config/components/LLMConfigurationPage')
);
export const MCPConfigPage = lazy(() => import('../pages/MCPConfigPage'));
export const SettingsPage = lazy(() => import('../pages/SettingsPage'));
export const ThemeDemoPage = lazy(() => import('../pages/ThemeDemoPage'));

// Specialized apps - carregamento sob demanda
export const WorkflowApp = lazy(() => import('../WorkflowApp'));
