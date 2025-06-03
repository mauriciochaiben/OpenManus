import React from 'react';
import {
  Layout,
  Typography,
  Space,
  Badge,
  Button,
  Avatar,
  Breadcrumb,
} from 'antd';
import { BellOutlined, UserOutlined, GlobalOutlined } from '@ant-design/icons';
import { useLocation } from 'react-router-dom';

const { Header: AntHeader } = Layout;
const { Text } = Typography;

const Header: React.FC = () => {
  const location = useLocation();

  const getPageTitle = (pathname: string) => {
    const routes: Record<string, string> = {
      '/': 'Home',
      '/dashboard': 'Dashboard',
      '/chat': 'AI Chat',
      '/knowledge': 'Base de Conhecimento',
      '/workflow': 'Workflows',
      '/llm-config': 'Configurações LLM',
      '/mcp-config': 'Configurações MCP',
      '/settings': 'Configurações',
    };
    return routes[pathname] || 'OpenManus';
  };

  const getBreadcrumbItems = (pathname: string) => {
    const items = [
      {
        title: (
          <Space>
            <GlobalOutlined />
            <span>OpenManus</span>
          </Space>
        ),
      },
    ];

    if (pathname !== '/') {
      items.push({
        title: <span>{getPageTitle(pathname)}</span>,
      });
    }

    return items;
  };

  return (
    <AntHeader
      style={{
        background: '#fff',
        padding: '0 32px',
        borderBottom: '1px solid #f0f0f0',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        height: '64px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
      }}
    >
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
        }}
      >
        <Breadcrumb
          items={getBreadcrumbItems(location.pathname)}
          style={{ marginBottom: '4px' }}
        />
        <Text
          style={{
            fontSize: '20px',
            fontWeight: 600,
            color: '#262626',
          }}
        >
          {getPageTitle(location.pathname)}
        </Text>
      </div>

      <Space size='large'>
        <Badge count={0} showZero={false}>
          <Button
            type='text'
            icon={<BellOutlined />}
            size='large'
            style={{
              border: 'none',
              color: '#595959',
            }}
          />
        </Badge>

        <Space>
          <Avatar
            size='small'
            icon={<UserOutlined />}
            style={{ backgroundColor: '#1890ff' }}
          />
          <Text
            style={{
              fontSize: '14px',
              color: '#595959',
            }}
          >
            Administrador
          </Text>
        </Space>
      </Space>
    </AntHeader>
  );
};

export default Header;
