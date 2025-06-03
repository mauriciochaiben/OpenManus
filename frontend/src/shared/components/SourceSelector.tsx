import React from "react";
import {
  Select,
  Card,
  Space,
  Typography,
  Tag,
  Button,
  Tooltip,
  Empty,
  Spin,
  Alert,
  Divider,
} from "antd";
import {
  FileTextOutlined,
  FilePdfOutlined,
  ReloadOutlined,
  ClearOutlined,
  BookOutlined,
  InfoCircleOutlined,
} from "@ant-design/icons";
import { useKnowledgeSources } from "../../features/knowledge/hooks/useKnowledgeSources";
import type { KnowledgeSource } from "../../features/knowledge/types/api";

const { Option } = Select;
const { Text } = Typography;

interface SourceSelectorProps {
  selectedSourceIds: string[];
  onSelectionChange: (sourceIds: string[]) => void;
  placeholder?: string;
  disabled?: boolean;
  showCard?: boolean;
  maxTagCount?: number;
  compact?: boolean;
}

const SourceSelector: React.FC<SourceSelectorProps> = ({
  selectedSourceIds,
  onSelectionChange,
  placeholder = "Select knowledge sources to enhance responses",
  disabled = false,
  showCard = true,
  maxTagCount = 2,
  compact = false,
}) => {
  const { completedSources, loading, error, refresh } = useKnowledgeSources();

  const getFileIcon = (source: KnowledgeSource) => {
    if (
      source.file_type === "application/pdf" ||
      source.filename.toLowerCase().endsWith(".pdf")
    ) {
      return <FilePdfOutlined style={{ color: "#ff4d4f", fontSize: "14px" }} />;
    }
    return <FileTextOutlined style={{ color: "#1890ff", fontSize: "14px" }} />;
  };

  const formatSourceLabel = (source: KnowledgeSource) => {
    const maxLength = compact ? 25 : 35;
    const displayName =
      source.filename.length > maxLength
        ? `${source.filename.substring(0, maxLength)}...`
        : source.filename;

    return (
      <Space size="small">
        {getFileIcon(source)}
        <span>{displayName}</span>
        {source.chunk_count && !compact && (
          <Tag color="blue" style={{ fontSize: "10px" }}>
            {source.chunk_count}
          </Tag>
        )}
      </Space>
    );
  };

  const handleClearAll = () => {
    onSelectionChange([]);
  };

  const getSelectedSourcesPreview = () => {
    if (selectedSourceIds.length === 0) return null;

    const selectedSources = completedSources.filter((source) =>
      selectedSourceIds.includes(source.id),
    );

    return (
      <div style={{ marginTop: "8px" }}>
        <Text type="secondary" style={{ fontSize: "12px" }}>
          Selected sources:
        </Text>
        <div style={{ marginTop: "4px" }}>
          <Space wrap size={[4, 4]}>
            {selectedSources.map((source) => (
              <Tooltip
                key={source.id}
                title={`${source.filename} (${source.chunk_count || 0} chunks)`}
              >
                <Tag
                  closable
                  onClose={() => {
                    const newSelection = selectedSourceIds.filter(
                      (id) => id !== source.id,
                    );
                    onSelectionChange(newSelection);
                  }}
                  style={{ fontSize: "11px" }}
                  icon={getFileIcon(source)}
                >
                  {source.filename.length > 15
                    ? `${source.filename.substring(0, 15)}...`
                    : source.filename}
                </Tag>
              </Tooltip>
            ))}
          </Space>
        </div>
      </div>
    );
  };

  const customTagRender = (props: any): React.ReactElement => {
    const { value, closable, onClose } = props;
    const source = completedSources.find((s) => s.id === value);

    if (!source) return <Tag>Unknown</Tag>;

    return (
      <Tooltip title={`${source.filename} (${source.chunk_count || 0} chunks)`}>
        <Tag
          closable={closable}
          onClose={onClose}
          style={{
            marginRight: 4,
            fontSize: "11px",
            display: "flex",
            alignItems: "center",
            gap: "4px",
          }}
        >
          {getFileIcon(source)}
          {source.filename.length > 12
            ? `${source.filename.substring(0, 12)}...`
            : source.filename}
        </Tag>
      </Tooltip>
    );
  };

  const selectorContent = (
    <Space direction="vertical" style={{ width: "100%" }} size="small">
      {!compact && (
        <>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <Space size="small">
              <BookOutlined style={{ color: "#1890ff" }} />
              <Text strong style={{ fontSize: "14px" }}>
                Knowledge Context
              </Text>
              <Tooltip title="Select documents to provide additional context for AI responses">
                <InfoCircleOutlined
                  style={{ color: "#666", fontSize: "12px" }}
                />
              </Tooltip>
            </Space>
            <Space size="small">
              {selectedSourceIds.length > 0 && (
                <Tooltip title="Clear all selected sources">
                  <Button
                    type="text"
                    size="small"
                    icon={<ClearOutlined />}
                    onClick={handleClearAll}
                    disabled={disabled}
                    style={{ fontSize: "12px" }}
                  >
                    Clear
                  </Button>
                </Tooltip>
              )}
              <Tooltip title="Refresh sources list">
                <Button
                  type="text"
                  size="small"
                  icon={<ReloadOutlined />}
                  onClick={refresh}
                  loading={loading}
                  disabled={disabled}
                  style={{ fontSize: "12px" }}
                />
              </Tooltip>
            </Space>
          </div>
          <Divider style={{ margin: "8px 0" }} />
        </>
      )}

      {error && (
        <Alert
          message="Error loading sources"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: "8px" }}
        />
      )}

      <Select
        mode="multiple"
        value={selectedSourceIds}
        onChange={onSelectionChange}
        placeholder={compact ? "Add context sources..." : placeholder}
        disabled={disabled || loading}
        style={{ width: "100%" }}
        size={compact ? "small" : "middle"}
        maxTagCount={maxTagCount}
        tagRender={customTagRender}
        maxTagPlaceholder={(omittedValues) => (
          <Tooltip title={`${omittedValues.length} more sources selected`}>
            <Tag style={{ fontSize: "11px" }}>+{omittedValues.length}</Tag>
          </Tooltip>
        )}
        filterOption={(input, option) => {
          const source = completedSources.find((s) => s.id === option?.value);
          return (
            source?.filename.toLowerCase().includes(input.toLowerCase()) ||
            false
          );
        }}
        optionLabelProp="label"
        notFoundContent={
          loading ? (
            <div style={{ textAlign: "center", padding: "12px" }}>
              <Spin size="small" />
              <div style={{ marginTop: "4px", fontSize: "12px" }}>
                Loading sources...
              </div>
            </div>
          ) : completedSources.length === 0 ? (
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description={
                <div style={{ fontSize: "12px" }}>
                  <div>No completed sources available</div>
                  <Text type="secondary" style={{ fontSize: "11px" }}>
                    Upload documents in Knowledge Management
                  </Text>
                </div>
              }
              style={{ padding: "12px" }}
            />
          ) : (
            <Empty
              image={Empty.PRESENTED_IMAGE_SIMPLE}
              description="No sources match your search"
              style={{ padding: "12px" }}
            />
          )
        }
      >
        {completedSources.map((source) => (
          <Option key={source.id} value={source.id} label={source.filename}>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <Tooltip title={source.filename}>
                {formatSourceLabel(source)}
              </Tooltip>
              {source.chunk_count && (
                <Text type="secondary" style={{ fontSize: "11px" }}>
                  {source.chunk_count} chunks
                </Text>
              )}
            </div>
          </Option>
        ))}
      </Select>

      {!compact &&
        selectedSourceIds.length === 0 &&
        completedSources.length > 0 && (
          <Text type="secondary" style={{ fontSize: "11px" }}>
            💡 Select sources to provide context and improve AI response
            accuracy
          </Text>
        )}

      {compact && getSelectedSourcesPreview()}
    </Space>
  );

  if (showCard) {
    return (
      <Card
        size="small"
        style={{
          marginBottom: compact ? "8px" : "16px",
          border:
            selectedSourceIds.length > 0 ? "1px solid #1890ff" : undefined,
        }}
        bodyStyle={{ padding: compact ? "12px" : "16px" }}
      >
        {selectorContent}
      </Card>
    );
  }

  return selectorContent;
};

export default SourceSelector;
