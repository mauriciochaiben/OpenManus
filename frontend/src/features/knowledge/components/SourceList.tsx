import React, { useState, useMemo, useEffect, useCallback } from "react";
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
  Spin,
  Empty,
  Result,
  Dropdown,
  MenuProps,
} from "antd";
import {
  EyeOutlined,
  DeleteOutlined,
  FileTextOutlined,
  FilePdfOutlined,
  FileImageOutlined,
  FileOutlined,
  SearchOutlined,
  ReloadOutlined,
  PlusOutlined,
  MoreOutlined,
  DownloadOutlined,
  EditOutlined,
  CopyOutlined,
  CheckCircleFilled,
  ClockCircleFilled,
  ExclamationCircleFilled,
  LoadingOutlined,
} from "@ant-design/icons";
import type { ColumnsType, TableProps } from "antd/es/table";
import { KnowledgeSource, ProcessingStatus } from "../types/api";
import {
  listSources,
  deleteSource,
  reprocessSource,
} from "../services/knowledgeApi";
import "./SourceList.css";

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
  const [error, setError] = useState<string | null>(null);
  const [searchText, setSearchText] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [fileTypeFilter, setFileTypeFilter] = useState<string>("all");

  // Fetch sources
  const fetchSources = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await listSources({ page_size: 100 });
      setSources(response.sources);
    } catch (error) {
      console.error("Error fetching sources:", error);
      setError("Erro ao carregar fontes. Tente novamente.");
      message.error("Erro ao carregar fontes");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSources();
  }, [fetchSources]);

  // Get file icon based on file extension
  const getFileIcon = (filename: string) => {
    const extension = filename.split(".").pop()?.toLowerCase();
    switch (extension) {
      case "pdf":
        return <FilePdfOutlined style={{ color: "#ff4d4f" }} />;
      case "txt":
      case "md":
      case "doc":
      case "docx":
        return <FileTextOutlined style={{ color: "#1890ff" }} />;
      case "jpg":
      case "jpeg":
      case "png":
      case "gif":
        return <FileImageOutlined style={{ color: "#52c41a" }} />;
      default:
        return <FileOutlined style={{ color: "#8c8c8c" }} />;
    }
  };

  // Get status tag with appropriate color and content
  const getStatusTag = (status: ProcessingStatus) => {
    const statusConfig = {
      pending: {
        color: "orange",
        text: "Pendente",
        icon: <ClockCircleFilled style={{ fontSize: "12px" }} />,
      },
      processing: {
        color: "blue",
        text: "Processando",
        icon: <LoadingOutlined style={{ fontSize: "12px" }} />,
      },
      completed: {
        color: "green",
        text: "Concluído",
        icon: <CheckCircleFilled style={{ fontSize: "12px" }} />,
      },
      failed: {
        color: "red",
        text: "Falhou",
        icon: <ExclamationCircleFilled style={{ fontSize: "12px" }} />,
      },
    };

    const config = statusConfig[status.status];

    if (status.status === "processing" && status.progress !== undefined) {
      return (
        <Space direction="vertical" size={4}>
          <Tag color={config.color} icon={config.icon}>
            {config.text}
          </Tag>
          <Progress percent={status.progress} size="small" strokeWidth={4} />
        </Space>
      );
    }

    return (
      <Tag color={config.color} icon={config.icon}>
        {config.text}
      </Tag>
    );
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
      return date.toLocaleDateString("pt-BR");
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
      message.success("Fonte excluída com sucesso");
      fetchSources(); // Refresh the list
    } catch (error) {
      message.error("Erro ao excluir fonte");
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
      message.success("Reprocessamento iniciado");
      fetchSources(); // Refresh the list
    } catch (error) {
      message.error("Erro ao reprocessar fonte");
    }
  };

  // Filter and search sources
  const filteredSources = useMemo(() => {
    return sources.filter((source: KnowledgeSource) => {
      const matchesSearch = source.filename
        .toLowerCase()
        .includes(searchText.toLowerCase());
      const matchesStatus =
        statusFilter === "all" || source.status.status === statusFilter;
      const fileExtension =
        source.filename.split(".").pop()?.toLowerCase() || "";
      const matchesFileType =
        fileTypeFilter === "all" || fileExtension === fileTypeFilter;

      return matchesSearch && matchesStatus && matchesFileType;
    });
  }, [sources, searchText, statusFilter, fileTypeFilter]);

  // Get unique file types for filter
  const fileTypes = useMemo(() => {
    const types = new Set(
      sources.map(
        (source: KnowledgeSource) =>
          source.filename.split(".").pop()?.toLowerCase() || "unknown",
      ),
    );
    return Array.from(types) as string[];
  }, [sources]);

  // Table columns configuration
  const columns: ColumnsType<KnowledgeSource> = [
    {
      title: "Arquivo",
      dataIndex: "filename",
      key: "filename",
      sorter: (a, b) => a.filename.localeCompare(b.filename),
      render: (filename: string, record: KnowledgeSource) => (
        <Space>
          <Avatar
            size="small"
            icon={getFileIcon(filename)}
            className="file-icon-avatar"
          />
          <div className="file-info">
            <div>
              <Text strong className="filename">
                {filename}
              </Text>
            </div>
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: "8px",
                marginTop: "2px",
              }}
            >
              {record.chunk_count && record.chunk_count > 0 && (
                <Space size={4}>
                  <Badge
                    count={record.chunk_count}
                    style={{ backgroundColor: "#52c41a" }}
                    size="small"
                  />
                  <Text type="secondary" style={{ fontSize: "11px" }}>
                    chunks
                  </Text>
                </Space>
              )}
              <Text type="secondary" style={{ fontSize: "11px" }}>
                {filename.split(".").pop()?.toUpperCase()}
              </Text>
            </div>
          </div>
        </Space>
      ),
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      width: 150,
      filters: [
        { text: "Pendente", value: "pending" },
        { text: "Processando", value: "processing" },
        { text: "Concluído", value: "completed" },
        { text: "Falhou", value: "failed" },
      ],
      onFilter: (value, record) => record.status.status === value,
      render: (status: ProcessingStatus) => getStatusTag(status),
    },
    {
      title: "Data de Upload",
      dataIndex: "upload_date",
      key: "upload_date",
      width: 150,
      sorter: (a, b) =>
        new Date(a.upload_date).getTime() - new Date(b.upload_date).getTime(),
      render: (date: string) => (
        <Tooltip title={new Date(date).toLocaleString("pt-BR")}>
          <Text type="secondary">{formatDate(date)}</Text>
        </Tooltip>
      ),
    },
    {
      title: "Ações",
      key: "actions",
      width: 160,
      render: (_, record: KnowledgeSource) => {
        const getDropdownMenuItems = (
          source: KnowledgeSource,
        ): MenuProps["items"] => [
          {
            key: "view",
            icon: <EyeOutlined />,
            label: "Ver Detalhes",
            onClick: () => onViewDetails?.(source),
          },
          {
            key: "edit",
            icon: <EditOutlined />,
            label: "Editar",
            disabled: true, // Placeholder for future feature
          },
          {
            key: "copy",
            icon: <CopyOutlined />,
            label: "Copiar ID",
            onClick: () => {
              navigator.clipboard.writeText(source.id);
              message.success("ID copiado para a área de transferência");
            },
          },
          {
            key: "download",
            icon: <DownloadOutlined />,
            label: "Baixar Arquivo",
            disabled: true, // Placeholder for future feature
          },
          {
            type: "divider",
          },
          ...(source.status.status === "failed"
            ? [
                {
                  key: "retry",
                  icon: <ReloadOutlined />,
                  label: "Tentar Novamente",
                  onClick: () => handleRetry(source),
                },
              ]
            : []),
          {
            key: "delete",
            icon: <DeleteOutlined />,
            label: "Excluir",
            danger: true,
            onClick: () => {
              // This will be handled by the popconfirm below
            },
          },
        ];

        return (
          <Space size="small">
            <Tooltip title="Ver Detalhes">
              <Button
                type="text"
                icon={<EyeOutlined />}
                onClick={() => onViewDetails?.(record)}
                size="small"
                className="source-action-btn"
              />
            </Tooltip>

            {record.status.status === "failed" && (
              <Tooltip title="Tentar Novamente">
                <Button
                  type="text"
                  icon={<ReloadOutlined />}
                  onClick={() => handleRetry(record)}
                  size="small"
                  className="source-action-btn retry-btn"
                />
              </Tooltip>
            )}

            <Dropdown
              menu={{ items: getDropdownMenuItems(record) }}
              trigger={["click"]}
              placement="bottomRight"
            >
              <Button
                type="text"
                icon={<MoreOutlined />}
                size="small"
                className="source-action-btn"
              />
            </Dropdown>

            <Popconfirm
              title="Excluir fonte"
              description="Tem certeza que deseja excluir esta fonte? Esta ação não pode ser desfeita."
              onConfirm={() => handleDelete(record)}
              okText="Sim"
              cancelText="Não"
              okType="danger"
            >
              <Tooltip title="Excluir">
                <Button
                  type="text"
                  danger
                  icon={<DeleteOutlined />}
                  size="small"
                  className="source-action-btn delete-btn"
                />
              </Tooltip>
            </Popconfirm>
          </Space>
        );
      },
    },
  ];

  const tableProps: TableProps<KnowledgeSource> = {
    columns,
    dataSource: filteredSources,
    rowKey: "id",
    loading: false, // Loading is handled separately with custom UI
    pagination: {
      pageSize: 10,
      showSizeChanger: true,
      showQuickJumper: true,
      showTotal: (total, range) => `${range[0]}-${range[1]} de ${total} fontes`,
      pageSizeOptions: ["10", "20", "50", "100"],
    },
    scroll: { x: 800 },
    size: "middle",
    className: "source-list-table",
    locale: {
      emptyText: "Nenhum dado", // Fallback, won't be shown due to custom empty handling
    },
  };

  return (
    <div className="source-list-container">
      {/* Filters */}
      <div className="source-list-filters">
        <Space wrap>
          <Input
            placeholder="Buscar por nome do arquivo..."
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
            placeholder="Filtrar por status"
          >
            <Option value="all">Todos os Status</Option>
            <Option value="pending">Pendente</Option>
            <Option value="processing">Processando</Option>
            <Option value="completed">Concluído</Option>
            <Option value="failed">Falhou</Option>
          </Select>

          <Select
            value={fileTypeFilter}
            onChange={setFileTypeFilter}
            style={{ width: 150 }}
            placeholder="Tipo de arquivo"
          >
            <Option value="all">Todos os Tipos</Option>
            {fileTypes.map((type: string) => (
              <Option key={type} value={type}>
                {type.toUpperCase()}
              </Option>
            ))}
          </Select>
        </Space>
      </div>

      {/* Content Area */}
      {loading ? (
        <div style={{ textAlign: "center", padding: "60px 20px" }}>
          <Spin size="large" />
          <div style={{ marginTop: "16px" }}>
            <Text type="secondary">Carregando fontes de conhecimento...</Text>
          </div>
        </div>
      ) : error ? (
        <Result
          status="error"
          title="Erro ao Carregar Fontes"
          subTitle={error}
          extra={[
            <Button
              type="primary"
              icon={<ReloadOutlined />}
              onClick={fetchSources}
              key="retry"
            >
              Tentar Novamente
            </Button>,
          ]}
        />
      ) : filteredSources.length === 0 && sources.length === 0 ? (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description={
            <Space direction="vertical">
              <Text strong>Nenhuma fonte encontrada</Text>
              <Text type="secondary">
                Comece adicionando uma fonte de conhecimento
              </Text>
            </Space>
          }
          style={{ padding: "60px 20px" }}
        >
          <Button type="primary" icon={<PlusOutlined />}>
            Adicionar Fonte
          </Button>
        </Empty>
      ) : filteredSources.length === 0 ? (
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description={
            <Space direction="vertical">
              <Text strong>Nenhum resultado encontrado</Text>
              <Text type="secondary">Tente ajustar os filtros de busca</Text>
            </Space>
          }
          style={{ padding: "40px 20px" }}
        >
          <Button
            onClick={() => {
              setSearchText("");
              setStatusFilter("all");
              setFileTypeFilter("all");
            }}
          >
            Limpar Filtros
          </Button>
        </Empty>
      ) : (
        <Table {...tableProps} />
      )}
    </div>
  );
};

export default SourceList;
