import React from "react";
import { Layout, Typography, Card, Empty } from "antd";

const { Content } = Layout;
const { Title } = Typography;

/**
 * Tasks page component - lazily loaded
 */
const TasksPage: React.FC = () => {
  return (
    <Content style={{ padding: "24px" }}>
      <Title level={2}>Task Management</Title>
      <Card>
        <Empty
          description="Task management components are being developed"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    </Content>
  );
};

export default TasksPage;
