import React from "react";
import { Layout, Typography } from "antd";
import { NoteList, NoteEditor } from "../features/notes/components";

const { Content } = Layout;
const { Title } = Typography;

/**
 * Notes page component - lazily loaded
 */
const NotesPage: React.FC = () => {
  return (
    <Content style={{ padding: "24px" }}>
      <Title level={2}>Notes Management</Title>
      <div
        style={{ display: "flex", gap: "16px", height: "calc(100vh - 200px)" }}
      >
        <div style={{ flex: 1 }}>
          <NoteList />
        </div>
        <div style={{ flex: 2 }}>
          <NoteEditor />
        </div>
      </div>
    </Content>
  );
};

export default NotesPage;
