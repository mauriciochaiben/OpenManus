import React, { useState } from "react";
import { Card, Typography, Space, Spin, Button, Tooltip } from "antd";
import { Handle, Position, NodeProps } from "reactflow";
import {
  MessageOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  CopyOutlined,
  ExpandOutlined,
} from "@ant-design/icons";

const { Text, Paragraph } = Typography;

interface ResponseNodeData {
  label: string;
  response?: string;
  description?: string;
  status?: "idle" | "running" | "completed" | "failed";
  error?: string;
  executionTime?: number;
  prompt?: string;
}

interface ResponseNodeProps extends NodeProps {
  data: ResponseNodeData;
}

const ResponseNode: React.FC<ResponseNodeProps> = ({ data, selected }) => {
  const [expanded, setExpanded] = useState(false);

  // Get status icon and color
  const getStatusDisplay = () => {
    switch (data.status) {
      case "running":
        return {
          icon: <LoadingOutlined spin style={{ color: "#1890ff" }} />,
          color: "#1890ff",
          text: "Processing",
          bgColor: "#e6f7ff",
        };
      case "completed":
        return {
          icon: <CheckCircleOutlined style={{ color: "#52c41a" }} />,
          color: "#52c41a",
          text: "Completed",
          bgColor: "#f6ffed",
        };
      case "failed":
        return {
          icon: <CloseCircleOutlined style={{ color: "#ff4d4f" }} />,
          color: "#ff4d4f",
          text: "Failed",
          bgColor: "#fff2f0",
        };
      default:
        return {
          icon: <MessageOutlined style={{ color: "#d9d9d9" }} />,
          color: "#d9d9d9",
          text: "Waiting",
          bgColor: "#fafafa",
        };
    }
  };

  const statusDisplay = getStatusDisplay();

  // Copy response to clipboard
  const handleCopy = () => {
    if (data.response) {
      navigator.clipboard.writeText(data.response);
    }
  };

  // Toggle expanded view
  const handleToggleExpanded = () => {
    setExpanded(!expanded);
  };

  return (
    <div style={{ minWidth: "300px", maxWidth: expanded ? "600px" : "400px" }}>
      {/* Input Handle */}
      <Handle
        type="target"
        position={Position.Left}
        style={{
          background: "#555",
          width: "12px",
          height: "12px",
          border: "2px solid #fff",
        }}
        isConnectable={true}
      />

      {/* Node Content */}
      <Card
        size="small"
        style={{
          border: selected ? "2px solid #1890ff" : "1px solid #d9d9d9",
          borderRadius: "8px",
          boxShadow: selected
            ? "0 4px 12px rgba(24, 144, 255, 0.3)"
            : "0 2px 8px rgba(0, 0, 0, 0.1)",
          backgroundColor: statusDisplay.bgColor,
        }}
        title={
          <Space style={{ width: "100%", justifyContent: "space-between" }}>
            <Space>
              {statusDisplay.icon}
              <Text strong>{data.label}</Text>
            </Space>
            <Space>
              <Text style={{ fontSize: "10px", color: statusDisplay.color }}>
                {statusDisplay.text}
              </Text>
              {data.executionTime && (
                <Text style={{ fontSize: "10px" }} type="secondary">
                  {data.executionTime}s
                </Text>
              )}
            </Space>
          </Space>
        }
        extra={
          <Space>
            {data.response && (
              <Tooltip title="Copy response">
                <Button
                  type="text"
                  size="small"
                  icon={<CopyOutlined />}
                  onClick={handleCopy}
                />
              </Tooltip>
            )}
            <Tooltip title={expanded ? "Collapse" : "Expand"}>
              <Button
                type="text"
                size="small"
                icon={<ExpandOutlined />}
                onClick={handleToggleExpanded}
              />
            </Tooltip>
          </Space>
        }
      >
        <Space direction="vertical" style={{ width: "100%" }} size="middle">
          {/* Description */}
          {data.description && (
            <Text type="secondary" style={{ fontSize: "12px" }}>
              {data.description}
            </Text>
          )}

          {/* Status Content */}
          {data.status === "running" && (
            <div style={{ textAlign: "center", padding: "20px" }}>
              <Spin size="large" />
              <div style={{ marginTop: "8px" }}>
                <Text type="secondary">Processing your request...</Text>
              </div>
            </div>
          )}

          {/* Response Content */}
          {data.response && (
            <div
              style={{
                padding: "12px",
                backgroundColor: "#fff",
                border: "1px solid #e8e8e8",
                borderRadius: "6px",
                maxHeight: expanded ? "none" : "200px",
                overflow: expanded ? "visible" : "hidden",
              }}
            >
              <Paragraph
                style={{
                  margin: 0,
                  fontSize: "13px",
                  lineHeight: "1.5",
                  whiteSpace: "pre-wrap",
                }}
                ellipsis={expanded ? false : { rows: 6, expandable: false }}
              >
                {data.response}
              </Paragraph>
            </div>
          )}

          {/* Error Content */}
          {data.error && (
            <div
              style={{
                padding: "12px",
                backgroundColor: "#fff2f0",
                border: "1px solid #ffccc7",
                borderRadius: "6px",
              }}
            >
              <Text type="danger" style={{ fontSize: "13px" }}>
                <strong>Error:</strong> {data.error}
              </Text>
            </div>
          )}

          {/* Waiting State */}
          {data.status === "idle" && !data.response && !data.error && (
            <div
              style={{
                padding: "20px",
                textAlign: "center",
                color: "#999",
                fontStyle: "italic",
              }}
            >
              <Text type="secondary">
                Connect a prompt node and execute to see results
              </Text>
            </div>
          )}

          {/* Character Count for Response */}
          {data.response && (
            <div style={{ textAlign: "right" }}>
              <Text type="secondary" style={{ fontSize: "11px" }}>
                {data.response.length} characters
              </Text>
            </div>
          )}
        </Space>
      </Card>

      {/* Output Handle */}
      <Handle
        type="source"
        position={Position.Right}
        style={{
          background: "#555",
          width: "12px",
          height: "12px",
          border: "2px solid #fff",
        }}
        isConnectable={true}
      />
    </div>
  );
};

export default ResponseNode;
