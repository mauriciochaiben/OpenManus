import React, { useState, useEffect, useCallback } from "react";
import {
  List,
  Card,
  Typography,
  Space,
  Tag,
  Button,
  Input,
  Select,
  Pagination,
  Empty,
  Spin,
  Result,
  Tooltip,
  Progress,
  Badge,
  Avatar,
  Dropdown,
  MenuProps,
} from "antd";
import {
  SearchOutlined,
  MoreOutlined,
  DownloadOutlined,
  DeleteOutlined,
  EyeOutlined,
  FileTextOutlined,
  FilePdfOutlined,
  AudioOutlined,
  CalendarOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  LoadingOutlined,
  SyncOutlined,
  FilterOutlined,
  ReloadOutlined,
} from "@ant-design/icons";
import { KnowledgeSource } from "../types/api";
import { listSources, reprocessSource } from "../services/knowledgeApi";

const { Search } = Input;
const { Option } = Select;
const { Text, Link, Paragraph } = Typography;

interface SourceListProps {
  onSourceSelect?: (source: KnowledgeSource) => void;
  onSourceView?: (source: KnowledgeSource) => void;
  refreshTrigger?: number;
  showActions?: boolean;
  pageSize?: number;
}

const SourceList: React.FC<SourceListProps> = ({
  onSourceSelect,
  onSourceView,
  refreshTrigger,
  showActions = true,
  pageSize = 10,
}) => {
  const [sources, setSources] = useState<KnowledgeSource[]>([]);
  const [loading, setLoading] = useState(true); // Initial loading true for skeleton
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [typeFilter, setTypeFilter] = useState<string>("all");

  // Fetch sources with filters and pagination
  const fetchSources = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await listSources({
        page: currentPage,
        page_size: pageSize,
        status: statusFilter !== "all" ? statusFilter : undefined,
        file_type: typeFilter !== "all" ? typeFilter : undefined,
      });

      setSources(response.sources);
      setTotal(response.total);
    } catch (error) {
      console.error("Error fetching sources:", error);
      setError("Falha ao carregar fontes de conhecimento. Tente novamente.");
    } finally {
      setLoading(false);
    }
  }, [currentPage, pageSize, searchQuery, statusFilter, typeFilter]);

  // Fetch on mount and when dependencies change
  useEffect(() => {
    fetchSources();
  }, [fetchSources, refreshTrigger]);

  // Reset page when filters change
  useEffect(() => {
    if (currentPage !== 1) {
      setCurrentPage(1);
    }
  }, [searchQuery, statusFilter, typeFilter]);

  // Handle search
  const handleSearch = (value: string) => {
    setSearchQuery(value);
  };

  // Handle retry
  const handleRetry = () => {
    setError(null);
    fetchSources();
  };

  // Handle retry processing
  const handleRetryProcessing = async (sourceId: string) => {
    try {
      await reprocessSource(sourceId);
      fetchSources();
    } catch (error) {
      console.error("Error retrying processing:", error);
    }
  };

  // Get file type icon
  const getFileIcon = (filename: string, fileType: string) => {
    const extension = filename.toLowerCase().split(".").pop();

    if (fileType.includes("pdf") || extension === "pdf") {
      return <FilePdfOutlined style={{ color: "#ff4d4f", fontSize: "20px" }} />;
    }
    if (
      fileType.includes("audio") ||
      ["mp3", "wav", "m4a", "aac"].includes(extension || "")
    ) {
      return <AudioOutlined style={{ color: "#722ed1", fontSize: "20px" }} />;
    }
    return <FileTextOutlined style={{ color: "#1890ff", fontSize: "20px" }} />;
  };

  // Get status configuration
  const getStatusConfig = (status: any) => {
    const statusStr = typeof status === "object" ? status.status : status;

    switch (statusStr) {
      case "completed":
        return {
          color: "success",
          icon: <CheckCircleOutlined />,
          text: "Completed",
        };
      case "processing":
        return {
          color: "processing",
          icon: <LoadingOutlined spin />,
          text: "Processing",
        };
      case "failed":
        return {
          color: "error",
          icon: <ExclamationCircleOutlined />,
          text: "Failed",
        };
      case "pending":
      default:
        return {
          color: "default",
          icon: <ClockCircleOutlined />,
          text: "Pending",
        };
    }
  };

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return "Today";
    if (diffDays === 2) return "Yesterday";
    if (diffDays <= 7) return `${diffDays} days ago`;

    return date.toLocaleDateString();
  };

  // Format file size
  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  };

  // Get dropdown menu items
  const getDropdownItems = (source: KnowledgeSource): MenuProps["items"] => [
    {
      key: "view",
      label: "View Details",
      icon: <EyeOutlined />,
      onClick: () => onSourceView?.(source),
    },
    {
      key: "download",
      label: "Download",
      icon: <DownloadOutlined />,
    },
    ...(source.status &&
    (typeof source.status === "object"
      ? source.status.status
      : source.status) === "failed"
      ? [
          {
            key: "retry",
            label: "Retry Processing",
            icon: <SyncOutlined />,
            onClick: () => handleRetryProcessing(source.id),
          },
        ]
      : []),
    {
      type: "divider" as const,
    },
    {
      key: "delete",
      label: "Delete",
      icon: <DeleteOutlined />,
      danger: true,
    },
  ];

  // Render source item
  const renderSourceItem = (source: KnowledgeSource) => {
    const statusConfig = getStatusConfig(source.status);

    return (
      <List.Item
        key={source.id}
        className="source-list-item"
        style={{
          padding: "16px",
          borderRadius: "8px",
          marginBottom: "8px",
          border: "1px solid #f0f0f0",
          backgroundColor: "#fafafa",
          cursor: onSourceSelect ? "pointer" : "default",
        }}
        onClick={() => onSourceSelect?.(source)}
        actions={
          showActions
            ? [
                <Dropdown
                  key="actions"
                  menu={{ items: getDropdownItems(source) }}
                  trigger={["click"]}
                >
                  <Button type="text" icon={<MoreOutlined />} />
                </Dropdown>,
              ]
            : undefined
        }
      >
        <List.Item.Meta
          avatar={
            <Badge
              count={source.chunk_count || 0}
              size="small"
              style={{ backgroundColor: "#52c41a" }}
            >
              <Avatar
                icon={getFileIcon(source.filename, source.file_type)}
                style={{ backgroundColor: "#f5f5f5" }}
              />
            </Badge>
          }
          title={
            <Space style={{ width: "100%", justifyContent: "space-between" }}>
              <Tooltip title={source.filename}>
                <Link
                  strong
                  onClick={(e) => {
                    e.stopPropagation();
                    onSourceView?.(source);
                  }}
                  style={{ maxWidth: "300px" }}
                  ellipsis
                >
                  {source.filename}
                </Link>
              </Tooltip>

              <Space>
                <Tag color={statusConfig.color} icon={statusConfig.icon}>
                  {statusConfig.text}
                </Tag>

                {source.size && (
                  <Text type="secondary" style={{ fontSize: "12px" }}>
                    {formatFileSize(source.size)}
                  </Text>
                )}
              </Space>
            </Space>
          }
          description={
            <Space direction="vertical" style={{ width: "100%" }} size="small">
              {/* Processing Progress */}
              {source.status &&
                typeof source.status === "object" &&
                source.status.status === "processing" &&
                source.status.progress && (
                  <Progress
                    percent={source.status.progress || 0}
                    size="small"
                    status="active"
                    format={(percent) => `${percent}% processed`}
                  />
                )}

              {/* Metadata */}
              <Space wrap>
                <Space size="small">
                  <CalendarOutlined style={{ color: "#666" }} />
                  <Text type="secondary" style={{ fontSize: "12px" }}>
                    {formatDate(source.upload_date)}
                  </Text>
                </Space>

                {source.chunk_count && (
                  <Space size="small">
                    <FileTextOutlined style={{ color: "#666" }} />
                    <Text type="secondary" style={{ fontSize: "12px" }}>
                      {source.chunk_count} chunks
                    </Text>
                  </Space>
                )}

                {source.status &&
                  typeof source.status === "object" &&
                  source.status.last_updated && (
                    <Space size="small">
                      <ClockCircleOutlined style={{ color: "#666" }} />
                      <Text type="secondary" style={{ fontSize: "12px" }}>
                        Updated {formatDate(source.status.last_updated)}
                      </Text>
                    </Space>
                  )}
              </Space>

              {/* Error Message */}
              {source.status &&
                typeof source.status === "object" &&
                source.status.status === "failed" &&
                source.status.error_message && (
                  <Text type="danger" style={{ fontSize: "12px" }}>
                    Error: {source.status.error_message}
                  </Text>
                )}

              {/* Description/Metadata */}
              {source.metadata?.description && (
                <Paragraph
                  ellipsis={{ rows: 2, expandable: false }}
                  style={{
                    margin: 0,
                    fontSize: "12px",
                    color: "#666",
                    maxWidth: "500px",
                  }}
                >
                  {source.metadata.description}
                </Paragraph>
              )}
            </Space>
          }
        />
      </List.Item>
    );
  };

  // Show error state
  if (error) {
    return (
      <div className="source-list-container">
        {/* Filters */}
        <Card
          size="small"
          style={{ marginBottom: "16px" }}
          bodyStyle={{ padding: "12px" }}
        >
          <Space wrap style={{ width: "100%" }}>
            <Search
              placeholder="Search sources..."
              allowClear
              onSearch={handleSearch}
              style={{ width: 300 }}
              enterButton={<SearchOutlined />}
              disabled
            />

            <Select
              placeholder="Status"
              value={statusFilter}
              onChange={setStatusFilter}
              style={{ width: 120 }}
              suffixIcon={<FilterOutlined />}
              disabled
            >
              <Option value="all">All Status</Option>
              <Option value="completed">Completed</Option>
              <Option value="processing">Processing</Option>
              <Option value="failed">Failed</Option>
              <Option value="pending">Pending</Option>
            </Select>

            <Select
              placeholder="File Type"
              value={typeFilter}
              onChange={setTypeFilter}
              style={{ width: 120 }}
              disabled
            >
              <Option value="all">All Types</Option>
              <Option value="pdf">PDF</Option>
              <Option value="text">Text</Option>
              <Option value="audio">Audio</Option>
            </Select>

            <Tooltip title="Refresh list">
              <Button
                icon={<SyncOutlined />}
                onClick={fetchSources}
                loading={loading}
              >
                Refresh
              </Button>
            </Tooltip>
          </Space>
        </Card>

        <Result
          status="error"
          title="Erro ao carregar fontes"
          subTitle={error}
          extra={[
            <Button
              key="retry"
              type="primary"
              icon={<ReloadOutlined />}
              onClick={handleRetry}
            >
              Tentar Novamente
            </Button>,
          ]}
        />
      </div>
    );
  }

  return (
    <div className="source-list-container">
      {/* Filters */}
      <Card
        size="small"
        style={{ marginBottom: "16px" }}
        bodyStyle={{ padding: "12px" }}
      >
        <Space wrap style={{ width: "100%" }}>
          <Search
            placeholder="Search sources..."
            allowClear
            onSearch={handleSearch}
            style={{ width: 300 }}
            enterButton={<SearchOutlined />}
          />

          <Select
            placeholder="Status"
            value={statusFilter}
            onChange={setStatusFilter}
            style={{ width: 120 }}
            suffixIcon={<FilterOutlined />}
          >
            <Option value="all">All Status</Option>
            <Option value="completed">Completed</Option>
            <Option value="processing">Processing</Option>
            <Option value="failed">Failed</Option>
            <Option value="pending">Pending</Option>
          </Select>

          <Select
            placeholder="File Type"
            value={typeFilter}
            onChange={setTypeFilter}
            style={{ width: 120 }}
          >
            <Option value="all">All Types</Option>
            <Option value="pdf">PDF</Option>
            <Option value="text">Text</Option>
            <Option value="audio">Audio</Option>
          </Select>

          <Tooltip title="Refresh list">
            <Button
              icon={<SyncOutlined />}
              onClick={fetchSources}
              loading={loading}
            >
              Refresh
            </Button>
          </Tooltip>
        </Space>
      </Card>

      {/* Sources List */}
      <Spin spinning={loading}>
        {!loading && sources.length === 0 ? (
          <Empty
            description={
              searchQuery || statusFilter !== "all" || typeFilter !== "all"
                ? "Nenhuma fonte encontrada com os filtros aplicados"
                : "Nenhuma fonte de conhecimento foi enviada ainda"
            }
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            style={{
              padding: "60px 20px",
              backgroundColor: "#fafafa",
              borderRadius: "8px",
            }}
          >
            {(searchQuery ||
              statusFilter !== "all" ||
              typeFilter !== "all") && (
              <Button
                type="primary"
                onClick={() => {
                  setSearchQuery("");
                  setStatusFilter("all");
                  setTypeFilter("all");
                }}
              >
                Limpar Filtros
              </Button>
            )}
          </Empty>
        ) : (
          <>
            <List
              dataSource={sources}
              renderItem={renderSourceItem}
              style={{ minHeight: "400px" }}
            />

            {/* Pagination */}
            {total > pageSize && (
              <div
                style={{
                  textAlign: "center",
                  marginTop: "24px",
                  padding: "16px",
                  backgroundColor: "#fafafa",
                  borderRadius: "8px",
                }}
              >
                <Pagination
                  current={currentPage}
                  total={total}
                  pageSize={pageSize}
                  onChange={setCurrentPage}
                  showSizeChanger={false}
                  showQuickJumper
                  showTotal={(total, range) =>
                    `${range[0]}-${range[1]} de ${total} fontes`
                  }
                />
              </div>
            )}
          </>
        )}
      </Spin>
    </div>
  );
};

export default SourceList;
