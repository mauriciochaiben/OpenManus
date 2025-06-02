import React from 'react';
import { Layout, Menu, Typography } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
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
    BranchesOutlined
} from '@ant-design/icons';

const { Sider } = Layout;
const { Title } = Typography;

const Sidebar: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();

    const menuItems = [
        // Core Navigation
        {
            key: 'core',
            type: 'group' as const,
            label: 'Principal',
            children: [
                {
                    key: '/',
                    icon: <HomeOutlined />,
                    label: 'Home',
                },
                {
                    key: '/dashboard',
                    icon: <DashboardOutlined />,
                    label: 'Dashboard',
                }
            ]
        },
        // Features
        {
            key: 'features',
            type: 'group' as const,
            label: 'Funcionalidades',
            children: [
                {
                    key: '/chat',
                    icon: <MessageOutlined />,
                    label: 'AI Chat',
                },
                {
                    key: '/knowledge',
                    icon: <BookOutlined />,
                    label: 'Base de Conhecimento',
                },
                {
                    key: '/workflow',
                    icon: <BranchesOutlined />,
                    label: 'Workflows',
                },
                {
                    key: '/canvas',
                    icon: <ExperimentOutlined />,
                    label: 'Canvas (Beta)',
                    disabled: true
                }
            ]
        },
        // Configuration
        {
            key: 'config',
            type: 'group' as const,
            label: 'Configurações',
            children: [
                {
                    key: '/llm-config',
                    icon: <ApiOutlined />,
                    label: 'Configurar LLM',
                },
                {
                    key: '/mcp-config',
                    icon: <CloudServerOutlined />,
                    label: 'Configurar MCP',
                },
                {
                    key: '/settings',
                    icon: <SettingOutlined />,
                    label: 'Configurações',
                }
            ]
        }
    ];

    const handleMenuClick = ({ key }: { key: string }) => {
        navigate(key);
    };

    return (
        <Sider
            width={250}
            className="sidebar"
            style={{
                background: '#001529',
                borderRight: '1px solid #303030',
                height: '100vh',
                position: 'fixed',
                left: 0,
                top: 0,
                bottom: 0,
                overflow: 'auto',
                zIndex: 1000,
                boxShadow: '2px 0 8px rgba(0,0,0,0.15)'
            }}
        >
            <div style={{ padding: '24px 16px' }}>
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    marginBottom: '32px',
                    padding: '12px',
                    background: 'rgba(255,255,255,0.1)',
                    borderRadius: '8px'
                }}>
                    <RocketOutlined style={{
                        fontSize: '28px',
                        color: '#1890ff',
                        marginRight: '12px',
                        textShadow: '0 0 10px rgba(24,144,255,0.5)'
                    }} />
                    <div>
                        <Title level={4} style={{
                            margin: 0,
                            color: '#fff',
                            fontSize: '18px',
                            fontWeight: 600
                        }}>
                            OpenManus
                        </Title>
                        <div style={{
                            color: '#8c8c8c',
                            fontSize: '12px',
                            marginTop: '2px'
                        }}>
                            AI Assistant Platform
                        </div>
                    </div>
                </div>

                <Menu
                    mode="inline"
                    selectedKeys={[location.pathname]}
                    items={menuItems}
                    onClick={handleMenuClick}
                    theme="dark"
                    style={{
                        border: 'none',
                        background: 'transparent',
                        fontSize: '14px'
                    }}
                />
            </div>
        </Sider>
    );
};

export default Sidebar;
