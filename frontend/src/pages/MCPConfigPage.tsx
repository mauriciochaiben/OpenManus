import React, { useState, useEffect } from 'react';
import {
  Card,
  Table,
  Button,
  Space,
  Typography,
  Tag,
  Modal,
  Form,
  Input,
  Switch,
  message,
  Popconfirm,
  Alert,
} from 'antd';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
} from '@ant-design/icons';
import {
  getMCPServers,
  createMCPServer,
  updateMCPServer,
  deleteMCPServer,
} from '../services/api';
import type { MCPServer, MCPServerConfig } from '../types';

const { Title, Text } = Typography;
const { TextArea } = Input;

const MCPConfigPage: React.FC = () => {
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [loading, setLoading] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingServer, setEditingServer] = useState<MCPServer | null>(null);
  const [form] = Form.useForm();

  const loadServers = async () => {
    setLoading(true);
    try {
      const response = await getMCPServers();
      setServers(response);
    } catch (error) {
      message.error('Failed to load MCP servers');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadServers();
  }, []);

  const handleCreateServer = () => {
    setEditingServer(null);
    form.resetFields();
    setModalVisible(true);
  };

  const handleEditServer = (server: MCPServer) => {
    setEditingServer(server);
    form.setFieldsValue({
      name: server.name,
      host: server.host,
      port: server.port,
      enabled: server.enabled,
      description: server.description,
    });
    setModalVisible(true);
  };

  const handleSubmit = async (values: any) => {
    try {
      const serverData: MCPServerConfig = {
        name: values.name,
        host: values.host,
        port: values.port,
        enabled: values.enabled || false,
        description: values.description || '',
      };

      if (editingServer) {
        await updateMCPServer(editingServer.id, serverData);
        message.success('MCP server updated successfully');
      } else {
        await createMCPServer(serverData);
        message.success('MCP server created successfully');
      }

      setModalVisible(false);
      loadServers();
    } catch (error) {
      message.error(
        `Failed to ${editingServer ? 'update' : 'create'} MCP server`
      );
    }
  };

  const handleDeleteServer = async (serverId: string) => {
    try {
      await deleteMCPServer(serverId);
      message.success('MCP server deleted successfully');
      loadServers();
    } catch (error) {
      message.error('Failed to delete MCP server');
    }
  };

  const handleToggleServer = async (server: MCPServer) => {
    try {
      await updateMCPServer(server.id, {
        ...server,
        enabled: !server.enabled,
      });
      message.success(`MCP server ${!server.enabled ? 'enabled' : 'disabled'}`);
      loadServers();
    } catch (error) {
      message.error('Failed to toggle MCP server');
    }
  };

  const columns = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: MCPServer) => (
        <Space direction='vertical' size='small'>
          <Text strong>{text}</Text>
          {record.description && (
            <Text type='secondary' style={{ fontSize: '12px' }}>
              {record.description}
            </Text>
          )}
        </Space>
      ),
    },
    {
      title: 'Host:Port',
      key: 'endpoint',
      render: (record: MCPServer) => (
        <Text code>
          {record.host}:{record.port}
        </Text>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status: string, record: MCPServer) => {
        const getStatusColor = () => {
          if (!record.enabled) return 'default';
          switch (status) {
            case 'connected':
              return 'success';
            case 'connecting':
              return 'processing';
            case 'error':
              return 'error';
            default:
              return 'warning';
          }
        };

        return (
          <Space>
            <Tag color={getStatusColor()}>
              {record.enabled ? status?.toUpperCase() || 'UNKNOWN' : 'DISABLED'}
            </Tag>
          </Space>
        );
      },
    },
    {
      title: 'Last Seen',
      dataIndex: 'last_seen',
      key: 'last_seen',
      render: (lastSeen: string) => {
        if (!lastSeen) return <Text type='secondary'>Never</Text>;
        const date = new Date(lastSeen);
        return <Text type='secondary'>{date.toLocaleString()}</Text>;
      },
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (record: MCPServer) => (
        <Space>
          <Button
            type='text'
            icon={
              record.enabled ? <PauseCircleOutlined /> : <PlayCircleOutlined />
            }
            onClick={() => handleToggleServer(record)}
            title={record.enabled ? 'Disable' : 'Enable'}
          />
          <Button
            type='text'
            icon={<EditOutlined />}
            onClick={() => handleEditServer(record)}
            title='Edit'
          />
          <Popconfirm
            title='Are you sure you want to delete this MCP server?'
            onConfirm={() => handleDeleteServer(record.id)}
            okText='Yes'
            cancelText='No'
          >
            <Button
              type='text'
              icon={<DeleteOutlined />}
              danger
              title='Delete'
            />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px', marginLeft: '250px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <Space direction='vertical' style={{ width: '100%' }} size='large'>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <div>
              <Title level={2}>MCP Server Configuration</Title>
              <Text type='secondary'>
                Manage Model Context Protocol servers for enhanced AI
                capabilities
              </Text>
            </div>
            <Space>
              <Button
                icon={<ReloadOutlined />}
                onClick={loadServers}
                loading={loading}
              >
                Refresh
              </Button>
              <Button
                type='primary'
                icon={<PlusOutlined />}
                onClick={handleCreateServer}
              >
                Add MCP Server
              </Button>
            </Space>
          </div>

          <Alert
            message='About MCP Servers'
            description="Model Context Protocol (MCP) servers extend the AI assistant's capabilities by providing access to external tools, data sources, and services. Configure and manage your MCP servers here."
            type='info'
            showIcon
          />

          <Card>
            <Table
              columns={columns}
              dataSource={servers}
              rowKey='id'
              loading={loading}
              pagination={{
                pageSize: 10,
                showSizeChanger: true,
                showTotal: (total) => `Total ${total} servers`,
              }}
            />
          </Card>

          <Modal
            title={editingServer ? 'Edit MCP Server' : 'Add MCP Server'}
            open={modalVisible}
            onOk={() => form.submit()}
            onCancel={() => setModalVisible(false)}
            okText={editingServer ? 'Update' : 'Create'}
            width={600}
          >
            <Form form={form} layout='vertical' onFinish={handleSubmit}>
              <Form.Item
                label='Server Name'
                name='name'
                rules={[
                  { required: true, message: 'Please enter a server name' },
                ]}
              >
                <Input placeholder='e.g., File Manager, Database Connector' />
              </Form.Item>

              <Form.Item
                label='Host'
                name='host'
                rules={[{ required: true, message: 'Please enter the host' }]}
              >
                <Input placeholder='localhost or IP address' />
              </Form.Item>

              <Form.Item
                label='Port'
                name='port'
                rules={[
                  { required: true, message: 'Please enter the port' },
                  {
                    type: 'number',
                    min: 1,
                    max: 65535,
                    message: 'Port must be between 1 and 65535',
                  },
                ]}
              >
                <Input type='number' placeholder='8080' />
              </Form.Item>

              <Form.Item label='Description' name='description'>
                <TextArea
                  rows={3}
                  placeholder='Optional description of what this MCP server provides'
                />
              </Form.Item>

              <Form.Item label='Enabled' name='enabled' valuePropName='checked'>
                <Switch />
              </Form.Item>
            </Form>
          </Modal>
        </Space>
      </div>
    </div>
  );
};

export default MCPConfigPage;
