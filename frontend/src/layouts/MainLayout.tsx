import React from "react";
import {
  Layout,
  Menu,
  Typography,
  Avatar,
  Dropdown,
  Badge,
  Button,
} from "antd";
import { useNavigate, useLocation, Outlet } from "react-router-dom";
import { useTheme } from "../theme";
import {
  HomeOutlined,
  SettingOutlined,
  CloudServerOutlined,
  RocketOutlined,
  MessageOutlined,
  DashboardOutlined,
  ApiOutlined,
  BookOutlined,
  ExperimentOutlined,
  BranchesOutlined,
  UserOutlined,
  BellOutlined,
  LogoutOutlined,
  ProfileOutlined,
  SunOutlined,
  MoonOutlined,
} from "@ant-design/icons";

const { Sider, Header, Content } = Layout;
const { Title } = Typography;

interface MainLayoutProps {
  children?: React.ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { isDarkMode, toggleTheme } = useTheme();

  // Menu items para o Sider
  const menuItems = [
    // Core Navigation
    {
      key: "core",
      type: "group" as const,
      label: "Principal",
      children: [
        {
          key: "/",
          icon: <HomeOutlined />,
          label: "Home",
        },
        {
          key: "/dashboard",
          icon: <DashboardOutlined />,
          label: "Dashboard",
        },
      ],
    },
    // Features
    {
      key: "features",
      type: "group" as const,
      label: "Funcionalidades",
      children: [
        {
          key: "/chat",
          icon: <MessageOutlined />,
          label: "Chat/Agente",
        },
        {
          key: "/knowledge",
          icon: <BookOutlined />,
          label: "Conhecimento",
        },
        {
          key: "/workflow",
          icon: <BranchesOutlined />,
          label: "Workflows",
        },
        {
          key: "/canvas",
          icon: <ExperimentOutlined />,
          label: "Canvas (Beta)",
          disabled: true,
        },
      ],
    },
    // Configuration
    {
      key: "config",
      type: "group" as const,
      label: "Configurações",
      children: [
        {
          key: "/llm-config",
          icon: <ApiOutlined />,
          label: "Configurar LLM",
        },
        {
          key: "/mcp-config",
          icon: <CloudServerOutlined />,
          label: "Configurar MCP",
        },
        {
          key: "/settings",
          icon: <SettingOutlined />,
          label: "Configurações",
        },
      ],
    },
  ];

  // Menu do usuário no Header
  const userMenuItems = [
    {
      key: "profile",
      icon: <ProfileOutlined />,
      label: "Perfil",
      onClick: () => navigate("/profile"),
    },
    {
      key: "settings",
      icon: <SettingOutlined />,
      label: "Configurações",
      onClick: () => navigate("/settings"),
    },
    { type: "divider" as const },
    {
      key: "logout",
      icon: <LogoutOutlined />,
      label: "Sair",
      onClick: () => {
        // Lógica de logout aqui
        console.log("Logout");
      },
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <Layout style={{ minHeight: "100vh" }}>
      {/* Sidebar */}
      <Sider
        width={250}
        style={{
          background: "#001529",
          borderRight: "1px solid #303030",
          height: "100vh",
          position: "fixed",
          left: 0,
          top: 0,
          bottom: 0,
          overflow: "auto",
          zIndex: 1000,
          boxShadow: "2px 0 8px rgba(0,0,0,0.15)",
        }}
      >
        {/* Logo e Título */}
        <div style={{ padding: "24px 16px" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              marginBottom: "32px",
              padding: "12px",
              background: "rgba(255,255,255,0.1)",
              borderRadius: "8px",
            }}
          >
            <RocketOutlined
              style={{
                fontSize: "28px",
                color: "#1890ff",
                marginRight: "12px",
                textShadow: "0 0 10px rgba(24,144,255,0.5)",
              }}
            />
            <div>
              <Title
                level={4}
                style={{
                  margin: 0,
                  color: "#fff",
                  fontSize: "18px",
                  fontWeight: 600,
                }}
              >
                OpenManus
              </Title>
              <div
                style={{
                  color: "#8c8c8c",
                  fontSize: "12px",
                  marginTop: "2px",
                }}
              >
                AI Assistant Platform
              </div>
            </div>
          </div>

          {/* Menu de Navegação */}
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={handleMenuClick}
            theme="dark"
            style={{
              border: "none",
              background: "transparent",
              fontSize: "14px",
            }}
          />
        </div>
      </Sider>

      {/* Layout Principal */}
      <Layout style={{ marginLeft: 250 }}>
        {/* Header */}
        <Header
          style={{
            background: "#fff",
            padding: "0 24px",
            borderBottom: "1px solid #f0f0f0",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
          }}
        >
          {/* Breadcrumb ou Título da Página */}
          <div>
            <Title level={4} style={{ margin: 0, color: "#262626" }}>
              {location.pathname === "/"
                ? "Home"
                : location.pathname === "/dashboard"
                  ? "Dashboard"
                  : location.pathname === "/chat"
                    ? "Chat/Agente"
                    : location.pathname === "/knowledge"
                      ? "Base de Conhecimento"
                      : location.pathname === "/workflow"
                        ? "Workflows"
                        : location.pathname === "/llm-config"
                          ? "Configurar LLM"
                          : location.pathname === "/mcp-config"
                            ? "Configurar MCP"
                            : location.pathname === "/settings"
                              ? "Configurações"
                              : "OpenManus"}
            </Title>
          </div>

          {/* Ações do Header */}
          <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
            {/* Botão de Troca de Tema */}
            <Button
              type="text"
              icon={isDarkMode ? <SunOutlined /> : <MoonOutlined />}
              onClick={toggleTheme}
              style={{ border: "none" }}
              title={isDarkMode ? "Ativar tema claro" : "Ativar tema escuro"}
            />

            {/* Notificações */}
            <Badge count={3} size="small">
              <Button
                type="text"
                icon={<BellOutlined />}
                style={{ border: "none" }}
              />
            </Badge>

            {/* Menu do Usuário */}
            <Dropdown
              menu={{ items: userMenuItems }}
              placement="bottomRight"
              trigger={["click"]}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  cursor: "pointer",
                  padding: "8px",
                  borderRadius: "6px",
                  transition: "background-color 0.2s",
                }}
              >
                <Avatar
                  size={32}
                  icon={<UserOutlined />}
                  style={{ marginRight: "8px" }}
                />
                <span style={{ fontSize: "14px", color: "#262626" }}>
                  Usuário
                </span>
              </div>
            </Dropdown>
          </div>
        </Header>

        {/* Content */}
        <Content
          style={{
            padding: "32px",
            background: "#f5f5f5",
            minHeight: "calc(100vh - 64px)",
            overflow: "auto",
          }}
        >
          {children || <Outlet />}
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
