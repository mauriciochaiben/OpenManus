import { Route } from "react-router-dom";
import LazyRouteWrapper from "./components/LazyRouteWrapper";
import * as LazyComponents from "./lazyComponents";

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
 * Organizadas por domínio para melhor performance
 */
export const FeatureRoutes = () => (
  <>
    {/* Communication & Interaction */}
    <Route
      path="/chat"
      element={
        <LazyRouteWrapper
          loadingMessage="Carregando chat..."
          componentName="ChatPage"
          featureName="Communication"
        >
          <LazyComponents.ChatPage />
        </LazyRouteWrapper>
      }
    />

    {/* Knowledge Management */}
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

    {/* Productivity & Organization */}
    <Route
      path="/notes"
      element={
        <LazyRouteWrapper
          loadingMessage="Carregando notas..."
          componentName="NotesPage"
        >
          <LazyComponents.NotesPage />
        </LazyRouteWrapper>
      }
    />
    <Route
      path="/tasks"
      element={
        <LazyRouteWrapper
          loadingMessage="Carregando tarefas..."
          componentName="TasksPage"
        >
          <LazyComponents.TasksPage />
        </LazyRouteWrapper>
      }
    />
    <Route
      path="/task/:id"
      element={
        <LazyRouteWrapper
          loadingMessage="Carregando detalhes da tarefa..."
          componentName="TaskDetailPage"
        >
          <LazyComponents.TaskDetailPage />
        </LazyRouteWrapper>
      }
    />

    {/* Agents & Automation */}
    <Route
      path="/agents"
      element={
        <LazyRouteWrapper
          loadingMessage="Carregando agentes..."
          componentName="AgentsPage"
        >
          <LazyComponents.AgentsPage />
        </LazyRouteWrapper>
      }
    />

    {/* Visual & Creative */}
    <Route
      path="/canvas"
      element={
        <LazyRouteWrapper
          loadingMessage="Carregando canvas..."
          componentName="CanvasPage"
        >
          <LazyComponents.CanvasPage />
        </LazyRouteWrapper>
      }
    />

    {/* Workflow Processing */}
    <Route
      path="/workflow"
      element={
        <LazyRouteWrapper
          loadingMessage="Carregando workflow..."
          componentName="WorkflowApp"
        >
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
    <Route
      path="/theme-demo"
      element={
        <LazyRouteWrapper loadingMessage="Carregando demonstração do tema...">
          <LazyComponents.ThemeDemoPage />
        </LazyRouteWrapper>
      }
    />
  </>
);
