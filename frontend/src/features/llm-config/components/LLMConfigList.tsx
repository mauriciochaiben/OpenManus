/**
 * LLM Configuration List Component
 * Displays and manages all LLM configurations
 */

import React, { useState } from 'react';
import {
  Table,
  Card,
  Space,
  Typography,
  Button,
  Tag,
  Dropdown,
  Modal,
  message,
  Tooltip,
  Badge,
  Statistic,
  Result,
  Spin,
} from 'antd';
import type { ColumnsType, TableProps } from 'antd/es/table';
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  DisconnectOutlined,
  MoreOutlined,
  StarOutlined,
  StarFilled,
  PlayCircleOutlined,
  PauseCircleOutlined,
  ApiOutlined,
} from '@ant-design/icons';

import { LLMConfiguration } from '../types';
import { useLLMConfigurations, useLLMTesting } from '../hooks/useLLMConfig';
import LLMConfigForm from './LLMConfigForm';

const { Title, Text } = Typography;

interface LLMConfigListProps {
  onConfigSelect?: (config: LLMConfiguration) => void;
}

const LLMConfigList: React.FC<LLMConfigListProps> = ({ onConfigSelect }) => {
  const { configurations, loading, actions } = useLLMConfigurations();
  const { testConfiguration, testResults } = useLLMTesting();

  const [modalVisible, setModalVisible] = useState(false);
  const [editingConfig, setEditingConfig] = useState<LLMConfiguration | null>(
    null
  );
  const [testingConfig, setTestingConfig] = useState<string | null>(null);

  const handleCreate = () => {
    setEditingConfig(null);
    setModalVisible(true);
  };

  const handleEdit = (config: LLMConfiguration) => {
    setEditingConfig(config);
    setModalVisible(true);
  };

  const handleDelete = (config: LLMConfiguration) => {
    Modal.confirm({
      title: 'Excluir Configuração',
      content: `Tem certeza que deseja excluir "${config.name}"? Esta ação não pode ser desfeita.`,
      okType: 'danger',
      onOk: async () => {
        try {
          await actions.delete(config.id);
          message.success('Configuração excluída com sucesso');
        } catch (error) {
          message.error('Falha ao excluir configuração');
        }
      },
    });
  };

  const handleSetDefault = async (config: LLMConfiguration) => {
    try {
      await actions.setDefault(config.id);
      message.success(`"${config.name}" definida como configuração padrão`);
    } catch (error) {
      message.error('Falha ao definir configuração padrão');
    }
  };

  const handleToggleActive = async (config: LLMConfiguration) => {
    try {
      await actions.toggle(config.id, !config.isActive);
      message.success(
        `Configuração ${config.isActive ? 'desativada' : 'ativada'}`
      );
    } catch (error) {
      message.error('Falha ao alterar status da configuração');
    }
  };

  const handleTest = async (config: LLMConfiguration) => {
    setTestingConfig(config.id);
    try {
      const result = await testConfiguration(config.id);
      if (result.success) {
        message.success(`Teste bem-sucedido! Latência: ${result.latency}ms`);
      } else {
        message.error(`Teste falhou: ${result.error}`);
      }
    } catch (error) {
      message.error('Teste falhou');
    } finally {
      setTestingConfig(null);
    }
  };

  const handleSave = () => {
    setModalVisible(false);
    setEditingConfig(null);
    actions.refetch();
  };

  const getProviderName = (providerId: string) => {
    // This would use the provider hook, but for simplicity showing ID
    return providerId;
  };

  const getStatusColor = (isActive: boolean) => {
    return isActive ? 'success' : 'default';
  };

  const getStatusText = (isActive: boolean) => {
    return isActive ? 'Ativa' : 'Inativa';
  };

  const getTestStatus = (configId: string) => {
    const result = testResults[configId];
    if (!result) return null;

    return result.success ? (
      <Badge status='success' text={`${result.latency}ms`} />
    ) : (
      <Badge status='error' text='Falhou' />
    );
  };

  const columns: ColumnsType<LLMConfiguration> = [
    {
      title: 'Nome',
      dataIndex: 'name',
      key: 'name',
      render: (text, record) => (
        <Space>
          <Text strong>{text}</Text>
          {record.isDefault && (
            <Tooltip title='Default Configuration'>
              <StarFilled style={{ color: '#faad14' }} />
            </Tooltip>
          )}
        </Space>
      ),
    },
    {
      title: 'Provedor',
      dataIndex: 'providerId',
      key: 'provider',
      render: (providerId) => (
        <Tag color='blue'>{getProviderName(providerId)}</Tag>
      ),
    },
    {
      title: 'Modelo',
      dataIndex: 'modelId',
      key: 'model',
      render: (modelId) => <Text code>{modelId}</Text>,
    },
    {
      title: 'Status',
      dataIndex: 'isActive',
      key: 'status',
      render: (isActive) => (
        <Tag color={getStatusColor(isActive)}>{getStatusText(isActive)}</Tag>
      ),
    },
    {
      title: 'Último Teste',
      key: 'lastTest',
      render: (_, record) =>
        getTestStatus(record.id) || <Text type='secondary'>Não testado</Text>,
    },
    {
      title: 'Atualizado',
      dataIndex: 'updatedAt',
      key: 'updatedAt',
      render: (date) => new Date(date).toLocaleDateString('pt-BR'),
    },
    {
      title: 'Ações',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Tooltip title='Testar Configuração'>
            <Button
              type='text'
              icon={<DisconnectOutlined />}
              onClick={() => handleTest(record)}
              loading={testingConfig === record.id}
              size='small'
            />
          </Tooltip>

          <Dropdown
            menu={{
              items: [
                {
                  key: 'edit',
                  label: 'Editar',
                  icon: <EditOutlined />,
                  onClick: () => handleEdit(record),
                },
                {
                  key: 'setDefault',
                  label: record.isDefault ? 'Padrão' : 'Definir como Padrão',
                  icon: record.isDefault ? <StarFilled /> : <StarOutlined />,
                  disabled: record.isDefault,
                  onClick: () => handleSetDefault(record),
                },
                {
                  key: 'toggle',
                  label: record.isActive ? 'Desativar' : 'Ativar',
                  icon: record.isActive ? (
                    <PauseCircleOutlined />
                  ) : (
                    <PlayCircleOutlined />
                  ),
                  onClick: () => handleToggleActive(record),
                },
                { type: 'divider' },
                {
                  key: 'delete',
                  label: 'Excluir',
                  icon: <DeleteOutlined />,
                  danger: true,
                  onClick: () => handleDelete(record),
                },
              ],
            }}
            trigger={['click']}
          >
            <Button type='text' icon={<MoreOutlined />} size='small' />
          </Dropdown>
        </Space>
      ),
    },
  ];

  const tableProps: TableProps<LLMConfiguration> = {
    columns,
    dataSource: configurations,
    rowKey: 'id',
    loading,
    pagination: {
      pageSize: 10,
      showSizeChanger: true,
      showQuickJumper: true,
      showTotal: (total, range) =>
        `${range[0]}-${range[1]} de ${total} configurações`,
    },
    onRow: (record) => ({
      onClick: () => onConfigSelect?.(record),
      style: { cursor: onConfigSelect ? 'pointer' : 'default' },
    }),
  };

  // Statistics
  const totalConfigs = configurations.length;
  const activeConfigs = configurations.filter((c) => c.isActive).length;
  const defaultConfig = configurations.find((c) => c.isDefault);

  return (
    <div>
      {/* Header with Stats */}
      <Card style={{ marginBottom: 16 }}>
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div>
            <Title level={4} style={{ margin: 0 }}>
              <ApiOutlined /> Configurações LLM
            </Title>
            <Text type='secondary'>
              Gerencie suas configurações de Large Language Model
            </Text>
          </div>

          <Space size='large'>
            <Statistic
              title='Total'
              value={totalConfigs}
              prefix={<ApiOutlined />}
            />
            <Statistic
              title='Ativas'
              value={activeConfigs}
              valueStyle={{ color: '#3f8600' }}
              prefix={<PlayCircleOutlined />}
            />
            <Button
              type='primary'
              icon={<PlusOutlined />}
              onClick={handleCreate}
            >
              Adicionar Configuração
            </Button>
          </Space>
        </div>
      </Card>

      {/* Default Configuration Info */}
      {defaultConfig && (
        <Card
          size='small'
          style={{ marginBottom: 16, backgroundColor: '#f6ffed' }}
        >
          <Space>
            <StarFilled style={{ color: '#faad14' }} />
            <Text>
              <Text strong>{defaultConfig.name}</Text> está definida como
              configuração padrão
            </Text>
            <Text type='secondary'>
              ({defaultConfig.providerId} - {defaultConfig.modelId})
            </Text>
          </Space>
        </Card>
      )}

      {/* Configurations Table */}
      <Card>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '60px 20px' }}>
            <Spin size='large' />
            <div style={{ marginTop: '16px' }}>
              <Text strong>Carregando configurações...</Text>
            </div>
            <div style={{ marginTop: '8px' }}>
              <Text type='secondary'>
                Aguarde enquanto buscamos suas configurações LLM
              </Text>
            </div>
          </div>
        ) : configurations.length > 0 ? (
          <Table {...tableProps} />
        ) : (
          <Result
            status='404'
            title='Nenhuma Configuração Encontrada'
            subTitle='Você ainda não possui configurações de LLM. Crie sua primeira configuração para começar.'
            icon={<ApiOutlined />}
            extra={[
              <Button
                type='primary'
                size='large'
                icon={<PlusOutlined />}
                onClick={handleCreate}
                key='create'
              >
                Criar Primeira Configuração
              </Button>,
            ]}
          />
        )}
      </Card>

      {/* Configuration Form Modal */}
      <Modal
        title={
          editingConfig ? 'Editar Configuração' : 'Adicionar Nova Configuração'
        }
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={800}
        destroyOnClose
      >
        <LLMConfigForm
          initialConfig={editingConfig || undefined}
          onSave={handleSave}
          onCancel={() => setModalVisible(false)}
          mode={editingConfig ? 'edit' : 'create'}
        />
      </Modal>
    </div>
  );
};

export default LLMConfigList;
