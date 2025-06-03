import React, { useState } from "react";
import {
  Upload,
  message,
  Card,
  Typography,
  Progress,
  Space,
  Button,
} from "antd";
import { InboxOutlined, FileOutlined, DeleteOutlined } from "@ant-design/icons";
import type { UploadProps, UploadFile } from "antd/es/upload/interface";
import { uploadDocument } from "../../services/api";
import type { UploadedDocument } from "../../types";

const { Dragger } = Upload;
const { Text, Title } = Typography;

interface DocumentUploadProps {
  onUploadSuccess?: (files: UploadedDocument[]) => void;
  maxFiles?: number;
  acceptedTypes?: string[];
}

const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onUploadSuccess,
  maxFiles = 10,
  acceptedTypes = [".pdf", ".doc", ".docx", ".txt", ".md"],
}) => {
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<{
    [key: string]: number;
  }>({});

  const uploadProps: UploadProps = {
    name: "file",
    multiple: true,
    maxCount: maxFiles,
    fileList,
    beforeUpload: (file) => {
      // Check file type
      const fileExtension = `.${file.name.split(".").pop()?.toLowerCase()}`;
      if (!acceptedTypes.includes(fileExtension)) {
        message.error(`File type ${fileExtension} is not supported`);
        return false;
      }

      // Check file size (50MB max)
      const isLt50M = file.size / 1024 / 1024 < 50;
      if (!isLt50M) {
        message.error("File must be smaller than 50MB!");
        return false;
      }

      return false; // Prevent auto upload
    },
    onChange: (info) => {
      setFileList(info.fileList);
    },
    onDrop: (e) => {
      console.log("Dropped files", e.dataTransfer.files);
    },
  };

  const handleUpload = async () => {
    if (fileList.length === 0) {
      message.warning("Please select files to upload");
      return;
    }

    setUploading(true);
    const uploadedFiles: UploadedDocument[] = [];

    try {
      for (const file of fileList) {
        if (file.originFileObj) {
          setUploadProgress((prev) => ({ ...prev, [file.uid]: 0 }));

          try {
            const response = await uploadDocument(
              file.originFileObj,
              (progress) => {
                setUploadProgress((prev) => ({
                  ...prev,
                  [file.uid]: progress,
                }));
              },
            );

            uploadedFiles.push(response);
            message.success(`${file.name} uploaded successfully`);
          } catch (error) {
            message.error(`Failed to upload ${file.name}`);
            console.error("Upload error:", error);
          }
        }
      }

      if (uploadedFiles.length > 0 && onUploadSuccess) {
        onUploadSuccess(uploadedFiles);
      }

      // Clear file list after successful upload
      setFileList([]);
      setUploadProgress({});
    } catch (error) {
      message.error("Upload failed");
      console.error("Upload error:", error);
    } finally {
      setUploading(false);
    }
  };

  const handleRemove = (file: UploadFile) => {
    const newFileList = fileList.filter((item) => item.uid !== file.uid);
    setFileList(newFileList);

    // Remove progress for this file
    setUploadProgress((prev) => {
      const newProgress = { ...prev };
      delete newProgress[file.uid];
      return newProgress;
    });
  };

  const clearAll = () => {
    setFileList([]);
    setUploadProgress({});
  };

  return (
    <Card title="Document Upload" className="document-upload-card">
      <Space direction="vertical" style={{ width: "100%" }} size="large">
        <Dragger {...uploadProps} style={{ padding: "40px 20px" }}>
          <p className="ant-upload-drag-icon">
            <InboxOutlined style={{ fontSize: "48px", color: "#1890ff" }} />
          </p>
          <p className="ant-upload-text">
            <Title level={4} style={{ margin: "16px 0 8px" }}>
              Click or drag files to this area to upload
            </Title>
          </p>
          <p className="ant-upload-hint">
            <Text type="secondary">
              Support for {acceptedTypes.join(", ")} files. Maximum file size:
              50MB. You can upload up to {maxFiles} files at once.
            </Text>
          </p>
        </Dragger>

        {fileList.length > 0 && (
          <div>
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                marginBottom: "16px",
              }}
            >
              <Text strong>Selected Files ({fileList.length})</Text>
              <Button
                type="link"
                icon={<DeleteOutlined />}
                onClick={clearAll}
                disabled={uploading}
              >
                Clear All
              </Button>
            </div>

            <Space direction="vertical" style={{ width: "100%" }}>
              {fileList.map((file) => (
                <Card
                  key={file.uid}
                  size="small"
                  style={{ background: "#fafafa" }}
                  actions={[
                    <Button
                      key="remove"
                      type="text"
                      icon={<DeleteOutlined />}
                      onClick={() => handleRemove(file)}
                      disabled={uploading}
                      danger
                    >
                      Remove
                    </Button>,
                  ]}
                >
                  <Space>
                    <FileOutlined />
                    <div style={{ flex: 1 }}>
                      <Text strong>{file.name}</Text>
                      <br />
                      <Text type="secondary">
                        {(file.size! / 1024 / 1024).toFixed(2)} MB
                      </Text>
                      {uploadProgress[file.uid] !== undefined && (
                        <Progress
                          percent={uploadProgress[file.uid]}
                          size="small"
                          style={{ marginTop: "8px" }}
                        />
                      )}
                    </div>
                  </Space>
                </Card>
              ))}
            </Space>
          </div>
        )}

        {fileList.length > 0 && (
          <Button
            type="primary"
            onClick={handleUpload}
            loading={uploading}
            size="large"
            block
          >
            Upload {fileList.length} file{fileList.length > 1 ? "s" : ""}
          </Button>
        )}
      </Space>
    </Card>
  );
};

export default DocumentUpload;
