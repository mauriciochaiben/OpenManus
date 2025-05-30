import React from 'react';
import { Layout, Typography, Space, Badge, Button } from 'antd';
import { BellOutlined, UserOutlined } from '@ant-design/icons';

const { Header: AntHeader } = Layout;
const { Text } = Typography;

const Header: React.FC = () => {
    return (
        <AntHeader
            style={{
                background: '#fff',
                padding: '0 24px',
                borderBottom: '1px solid #f0f0f0',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                position: 'sticky',
                top: 0,
                zIndex: 100,
                marginLeft: 250, // Account for sidebar width
            }}
        >
            <div>
                <Text style={{ fontSize: '16px', fontWeight: 500 }}>
                    AI Assistant Dashboard
                </Text>
            </div>

            <Space size="middle">
                <Badge count={0} showZero={false}>
                    <Button
                        type="text"
                        icon={<BellOutlined />}
                        style={{ border: 'none' }}
                    />
                </Badge>

                <Button
                    type="text"
                    icon={<UserOutlined />}
                    style={{ border: 'none' }}
                >
                    User
                </Button>
            </Space>
        </AntHeader>
    );
};

export default Header;
