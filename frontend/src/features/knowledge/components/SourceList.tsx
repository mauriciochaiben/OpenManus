import React, { useState, useMemo, useEffect, useCallback } from 'react';
import {
  Table,
  Tag,
  Button,
  Popconfirm,
  Space,
  Input,
  Select,
  Typography,
  Tooltip,
  Badge,
  Progress,
  message,
  Avatar,
} from 'antd';
import {
  EyeOutlined,
  DeleteOutlined,
  FileTextOutlined,
  FilePdfOutlined,
  FileImageOutlined,
  FileOutlined,
  SearchOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import type { ColumnsType, TableProps } from 'antd/es/table';
import { KnowledgeSource, ProcessingStatus } from '../types/api';
import {
  listSources,
  deleteSource,
  reprocessSource,
} from '../services/knowledgeApi';
import './SourceList.css';

const { Text } = Typography;
const { Option } = Select;

interface SourceListProps {
  onViewDetails?: (source: KnowledgeSource) => void;
  onDelete?: (sourceId: string) => Promise<void>;
  onRetry?: (sourceId: string) => Promise<void>;
}

const SourceList: React.FC<SourceListProps> = ({
  onViewDetails,
  onDelete,
  onRetry,
}) => {
  const [sources, setSources] = useState<KnowledgeSource[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [fileTypeFilter, setFileTypeFilter] = useState<string>('all');

  // Fetch sources
  const fetchSources = useCallback(async () => {
    try {
      setLoading(true);
      const response = await listSources({ page_size: 100 });
      setSources(response.sources);
    } catch (error) {
      console.error('Error fetching sources:', error);
      message.error('Erro ao carregar fontes');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSources();
  }, [fetchSources]);

  // Get file icon based on file extension
  const getFileIcon = (filename: string) => {
    const extension = filename.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'pdf':
        return <FilePdfOutlined style={{ color: '#ff4d4f' }} />;
      case 'txt':
      case 'md':
      case 'doc':
      case 'docx':
        return <FileTextOutlined style={{ color: '#1890ff' }} />;
      case 'jpg':
      case 'jpeg':
      case 'png':
      case 'gif':
        return <FileImageOutlined style={{ color: '#52c41a' }} />;
      default:
        return <FileOutlined style={{ color: '#8c8c8c' }} />;
    }
  };

  // Get status tag with appropriate color and content
  const getStatusTag = (status: ProcessingStatus) => {
    const statusConfig = {
      pending: { color: 'orange', text: 'Pendente' },
      processing: { color: 'blue', text: 'Processando' },
      completed: { color: 'green', text: 'Concluído' },
      failed: { color: 'red', text: 'Falhou' },
    };

    const config = statusConfig[status.status];

    if (status.status === 'processing' && status.progress !== undefined) {
      return (
        <Space direction='vertical' size={4}>
          <Tag color={config.color}>{config.text}</Tag>
          <Progress percent={status.progress} size='small' strokeWidth={4} />
        </Space>
      );
    }

    return <Tag color={config.color}>{config.text}</Tag>;
  };

  // Format date in a user-friendly way
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now.getTime() - date.getTime()) / (1000 * 3600);

    if (diffInHours < 24) {
      return `${Math.floor(diffInHours)}h atrás`;
    } else if (diffInHours < 24 * 7) {
      return `${Math.floor(diffInHours / 24)}d atrás`;
    } else {
      return date.toLocaleDateString('pt-BR');
    }
  };

  // Handle delete action
  const handleDelete = async (source: KnowledgeSource) => {
    try {
      if (onDelete) {
        await onDelete(source.id);
      } else {
        await deleteSource(source.id);
      }
      message.success('Fonte excluída com sucesso');
      fetchSources(); // Refresh the list
    } catch (error) {
      message.error('Erro ao excluir fonte');
    }
  };

  // Handle retry action
  const handleRetry = async (source: KnowledgeSource) => {
    try {
      if (onRetry) {
        await onRetry(source.id);
      } else {
        await reprocessSource(source.id);
      }
      message.success('Reprocessamento iniciado');
      fetchSources(); // Refresh the list
    } catch (error) {
      message.error('Erro ao reprocessar fonte');
    }
  };

  // Filter and search sources
  const filteredSources = useMemo(() => {
    return sources.filter((source: KnowledgeSource) => {
      const matchesSearch = source.filename
        .toLowerCase()
        .includes(searchText.toLowerCase());
      const matchesStatus =
        statusFilter === 'all' || source.status.status === statusFilter;
      const fileExtension =
        source.filename.split('.').pop()?.toLowerCase() || '';
      const matchesFileType =
        fileTypeFilter === 'all' || fileExtension === fileTypeFilter;

      return matchesSearch && matchesStatus && matchesFileType;
    });
  }, [sources, searchText, statusFilter, fileTypeFilter]);

  // Get unique file types for filter
  const fileTypes = useMemo(() => {
    const types = new Set(
      sources.map(
        (source: KnowledgeSource) =>
          source.filename.split('.').pop()?.toLowerCase() || 'unknown'
      )
    );
    return Array.from(types) as string[];
  }, [sources]);

  // Table columns configuration
  const columns: ColumnsType<KnowledgeSource> = [
    {
      title: 'Arquivo',
      dataIndex: 'filename',
      key: 'filename',
      sorter: (a, b) => a.filename.localeCompare(b.filename),
      render: (filename: string, record: KnowledgeSource) => (
        <Space>
          <Avatar size='small' icon={getFileIcon(filename)} />
          <div>
            <Text strong>{filename}</Text>
            {record.chunk_count && record.chunk_count > 0 && (
              <div>
                <Badge
                  count={record.chunk_count}
                  style={{ backgroundColor: '#52c41a' }}
                  size='small'
                />
                <Text type='secondary' style={{ marginLeft: 4 }}>
                  chunks
                </Text>
              </div>
            )}
          </div>
        </Space>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 150,
      filters: [
        { text: 'Pendente', value: 'pending' },
        { text: 'Processando', value: 'processing' },
        { text: 'Concluído', value: 'completed' },
        { text: 'Falhou', value: 'failed' },
      ],
      onFilter: (value, record) => record.status.status === value,
      render: (status: ProcessingStatus) => getStatusTag(status),
    },
    {
      title: 'Data de Upload',
      dataIndex: 'upload_date',
      key: 'upload_date',
      width: 150,
      sorter: (a, b) =>
        new Date(a.upload_date).getTime() - new Date(b.upload_date).getTime(),
      render: (date: string) => (
        <Tooltip title={new Date(date).toLocaleString('pt-BR')}>
          <Text type='secondary'>{formatDate(date)}</Text>
        </Tooltip>
      ),
    },
    {
      title: 'Ações',
      key: 'actions',
      width: 120,
      render: (_, record: KnowledgeSource) => (
        <Space size='small'>
          <Tooltip title='Ver Detalhes'>
            <Button
              type='text'
              icon={<EyeOutlined />}
              onClick={() => onViewDetails?.(record)}
              size='small'
            />
          </Tooltip>

          {record.status.status === 'failed' && (
            <Tooltip title='Tentar Novamente'>
              <Button
                type='text'
                icon={<ReloadOutlined />}
                onClick={() => handleRetry(record)}
                size='small'
              />
            </Tooltip>
          )}

          <Popconfirm
            title='Excluir fonte'
            description='Tem certeza que deseja excluir esta fonte? Esta ação não pode ser desfeita.'
            onConfirm={() => handleDelete(record)}
            okText='Sim'
            cancelText='Não'
            okType='danger'
          >
            <Tooltip title='Excluir'>
              <Button
                type='text'
                danger
                icon={<DeleteOutlined />}
                size='small'
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  const tableProps: TableProps<KnowledgeSource> = {
    columns,
    dataSource: filteredSources,
    rowKey: 'id',
    loading,
    pagination: {
      pageSize: 10,
      showSizeChanger: true,
      showQuickJumper: true,
      showTotal: (total, range) => `${range[0]}-${range[1]} de ${total} fontes`,
      pageSizeOptions: ['10', '20', '50', '100'],
    },
    scroll: { x: 800 },
    size: 'middle',
    className: 'source-list-table',
  };

  return (
    <div className='source-list-container'>
      {/* Filters */}
      <div className='source-list-filters'>
        <Space wrap>
          <Input
            placeholder='Buscar por nome do arquivo...'
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: 250 }}
            allowClear
          />

          <Select
            value={statusFilter}
            onChange={setStatusFilter}
            style={{ width: 150 }}
            placeholder='Filtrar por status'
          >
            <Option value='all'>Todos os Status</Option>
            <Option value='pending'>Pendente</Option>
            <Option value='processing'>Processando</Option>
            <Option value='completed'>Concluído</Option>
            <Option value='failed'>Falhou</Option>
          </Select>

          <Select
            value={fileTypeFilter}
            onChange={setFileTypeFilter}
            style={{ width: 150 }}
            placeholder='Tipo de arquivo'
          >
            <Option value='all'>Todos os Tipos</Option>
            {fileTypes.map((type: string) => (
              <Option key={type} value={type}>
                {type.toUpperCase()}
              </Option>
            ))}
          </Select>
        </Space>
      </div>

      {/* Table */}
      <Table {...tableProps} />
    </div>
  );
};

export default SourceList;
