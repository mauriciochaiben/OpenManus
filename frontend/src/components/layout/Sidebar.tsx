import React from 'react';
import { Layout, Menu, Typography } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
    HomeOutlined,
    SettingOutlined,
    CloudServerOutlined,
    RocketOutlined
} from '@ant-design/icons';

const { Sider } = Layout;
const { Title } = Typography;

const Sidebar: React.FC = () => {
    const navigate = useNavigate();
    const location = useLocation();

    const menuItems = [
        {
            key: '/',
            icon: <HomeOutlined />,
            label: 'Home',
        },
        {
            key: '/mcp-config',
            icon: <CloudServerOutlined />,
            label: 'MCP Config',
        },
        {
            key: '/settings',
            icon: <SettingOutlined />,
            label: 'Settings',
        },
    ];

    const handleMenuClick = ({ key }: { key: string }) => {
        navigate(key);
    };

    return (
        <Sider
            width={250}
            className="sidebar"
            style={{
                background: '#fff',
                borderRight: '1px solid #f0f0f0',
                height: '100vh',
                position: 'fixed',
                left: 0,
                top: 0,
                bottom: 0,
                overflow: 'auto',
                zIndex: 1000,
            }}
        >
            <div style={{ padding: '24px 16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '24px' }}>
                    <RocketOutlined style={{ fontSize: '24px', color: '#1890ff', marginRight: '12px' }} />
                    <Title level={4} style={{ margin: 0, color: '#1890ff' }}>
                        OpenManus
                    </Title>
                </div>

                <Menu
                    mode="inline"
                    selectedKeys={[location.pathname]}
                    items={menuItems}
                    onClick={handleMenuClick}
                    style={{
                        border: 'none',
                        background: 'transparent',
                    }}
                />
            </div>
        </Sider>
    );
};

export default Sidebar;
