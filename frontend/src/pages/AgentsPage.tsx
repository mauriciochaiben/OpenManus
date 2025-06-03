import React from 'react';
import { Layout, Typography, Card, Empty } from 'antd';

const { Content } = Layout;
const { Title } = Typography;

/**
 * Agents page component - lazily loaded
 */
const AgentsPage: React.FC = () => {
  return (
    <Content style={{ padding: '24px' }}>
      <Title level={2}>Agents Management</Title>
      <Card>
        <Empty
          description='Agent management components are being developed'
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    </Content>
  );
};

export default AgentsPage;
