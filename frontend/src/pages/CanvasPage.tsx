import React from 'react';
import { Layout } from 'antd';
import { CanvasWorkspace } from '../features/canvas/components';

const { Content } = Layout;

/**
 * Canvas page component - lazily loaded
 */
const CanvasPage: React.FC = () => {
  return (
    <Layout style={{ height: '100vh' }}>
      <Content style={{ padding: 0 }}>
        <CanvasWorkspace />
      </Content>
    </Layout>
  );
};

export default CanvasPage;
