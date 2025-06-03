import React, { useState } from 'react';
import {
  Upload,
  message,
  Progress,
  Typography,
  Card,
  Space,
  Alert,
  Button,
  Spin,
} from 'antd';
import {
  InboxOutlined,
  FileTextOutlined,
  FilePdfOutlined,
  CloudUploadOutlined,
  LoadingOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  UploadOutlined,
  AudioOutlined,
} from '@ant-design/icons';
import type { UploadProps, UploadFile, RcFile } from 'antd/es/upload/interface';
import { uploadSource, ApiError } from '../services/knowledgeApi';
import type { UploadSourceResponse } from '../types/api';

const { Dragger } = Upload;
const { Text, Paragraph } = Typography;

interface SourceUploaderProps {
  onUploadSuccess?: (response: UploadSourceResponse) => void;
  onUploadError?: (error: ApiError) => void;
  disabled?: boolean;
  maxFileSize?: number; // in MB
}

interface UploadProgress {
  percent: number;
  status: 'uploading' | 'done' | 'error';
  fileName: string;
}

const SourceUploader: React.FC<SourceUploaderProps> = ({
  onUploadSuccess,
  onUploadError,
  disabled = false,
  maxFileSize = 50, // 50MB default
}) => {
  const [fileList, setFileList] = useState<UploadFile[]>([]);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress | null>(
    null
  );
  const [isUploading, setIsUploading] = useState(false);

  // File type validation
  const beforeUpload = (file: RcFile): boolean => {
    const allowedTypes = [
      'application/pdf',
      'text/plain',
      'audio/mpeg',
      'audio/wav',
      'audio/x-wav',
      'audio/mp4',
      'audio/aac',
      'audio/ogg',
      'audio/flac',
      'audio/webm',
    ];
    const allowedExtensions = [
      '.pdf',
      '.txt',
      '.mp3',
      '.wav',
      '.m4a',
      '.aac',
      '.ogg',
      '.flac',
      '.webm',
    ];

    const isValidType =
      allowedTypes.includes(file.type) ||
      allowedExtensions.some((ext) => file.name.toLowerCase().endsWith(ext));

    if (!isValidType) {
      message.error({
        content:
          'Only PDF, TXT, and Audio files (MP3, WAV, M4A, AAC, OGG, FLAC, WEBM) are allowed!',
        icon: <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
      });
      return false;
    }

    const isValidSize = file.size / 1024 / 1024 < maxFileSize;
    if (!isValidSize) {
      message.error({
        content: `File must be smaller than ${maxFileSize}MB!`,
        icon: <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
      });
      return false;
    }

    return true;
  };

  // Custom upload request
  const customRequest: UploadProps['customRequest'] = async (options) => {
    const { file, onProgress, onSuccess, onError } = options;
    const uploadFile = file as RcFile;

    try {
      setIsUploading(true);
      setUploadProgress({
        percent: 0,
        status: 'uploading',
        fileName: uploadFile.name,
      });

      // Simulate upload progress with more realistic increments
      let currentProgress = 0;
      const progressInterval = setInterval(() => {
        if (currentProgress < 85) {
          currentProgress += Math.random() * 15;
          setUploadProgress((prev) => {
            if (!prev) return prev;
            return {
              ...prev,
              percent: Math.min(currentProgress, 85),
            };
          });
          onProgress?.({ percent: Math.min(currentProgress, 85) });
        }
      }, 300);

      // Call the API
      const response = await uploadSource({
        file: uploadFile,
        metadata: {
          originalName: uploadFile.name,
          uploadedAt: new Date().toISOString(),
          fileSize: uploadFile.size,
        },
      });

      // Clear progress interval
      clearInterval(progressInterval);

      // Complete progress
      setUploadProgress({
        percent: 100,
        status: 'done',
        fileName: uploadFile.name,
      });
      onProgress?.({ percent: 100 });

      // Success callbacks
      onSuccess?.(response);
      onUploadSuccess?.(response);

      message.success({
        content: `${uploadFile.name} uploaded successfully!`,
        icon: <CheckCircleOutlined style={{ color: '#52c41a' }} />,
      });

      // Clear progress after delay
      setTimeout(() => {
        setUploadProgress(null);
        setIsUploading(false);
        setFileList([]);
      }, 3000);
    } catch (error) {
      const apiError = error as ApiError;

      setUploadProgress({
        percent: 0,
        status: 'error',
        fileName: uploadFile.name,
      });

      onError?.({
        name: 'UploadError',
        message: apiError.message,
      } as any);
      onUploadError?.(apiError);

      message.error({
        content: `Upload failed: ${apiError.message}`,
        icon: <CloseCircleOutlined style={{ color: '#ff4d4f' }} />,
      });

      setTimeout(() => {
        setUploadProgress(null);
        setIsUploading(false);
      }, 5000);
    }
  };

  // Handle file list changes
  const handleChange: UploadProps['onChange'] = (info) => {
    let newFileList = [...info.fileList];
    newFileList = newFileList.slice(-1); // Show only the last uploaded file
    setFileList(newFileList);
  };

  // Remove file handler
  const handleRemove = (): boolean => {
    setFileList([]);
    setUploadProgress(null);
    return true;
  };

  const getFileIcon = (fileName: string) => {
    const lowerName = fileName.toLowerCase();
    if (lowerName.endsWith('.pdf')) {
      return <FilePdfOutlined style={{ color: '#ff4d4f', fontSize: '20px' }} />;
    }
    if (lowerName.match(/\.(mp3|wav|m4a|aac|ogg|flac|webm)$/)) {
      return <AudioOutlined style={{ color: '#722ed1', fontSize: '20px' }} />;
    }
    return <FileTextOutlined style={{ color: '#1890ff', fontSize: '20px' }} />;
  };

  const getProgressIcon = (status: UploadProgress['status']) => {
    switch (status) {
      case 'uploading':
        return <LoadingOutlined style={{ color: '#1890ff' }} />;
      case 'done':
        return <CheckCircleOutlined style={{ color: '#52c41a' }} />;
      case 'error':
        return <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return <UploadOutlined />;
    }
  };

  return (
    <Card
      title={
        <Space>
          <CloudUploadOutlined />
          <span>Upload Knowledge Source</span>
        </Space>
      }
      style={{ width: '100%' }}
    >
      <Space direction='vertical' size='large' style={{ width: '100%' }}>
        <Dragger
          name='file'
          multiple={false}
          fileList={fileList}
          beforeUpload={beforeUpload}
          customRequest={customRequest}
          onChange={handleChange}
          onRemove={handleRemove}
          disabled={disabled || isUploading}
          showUploadList={false}
          accept='.pdf,.txt,.mp3,.wav,.m4a,.aac,.ogg,.flac,.webm'
          style={{
            background: isUploading ? '#f0f2f5' : '#fafafa',
            border: isUploading ? '2px dashed #d9d9d9' : '2px dashed #d9d9d9',
          }}
        >
          <div style={{ padding: '20px' }}>
            <p className='ant-upload-drag-icon'>
              {isUploading ? (
                <Spin
                  indicator={<LoadingOutlined style={{ fontSize: 48 }} />}
                />
              ) : (
                <InboxOutlined style={{ fontSize: 48, color: '#1890ff' }} />
              )}
            </p>
            <p
              className='ant-upload-text'
              style={{ fontSize: '16px', fontWeight: 500 }}
            >
              {isUploading
                ? 'Uploading...'
                : 'Click or drag file to this area to upload'}
            </p>
            <p className='ant-upload-hint' style={{ color: '#666' }}>
              Support for PDF, TXT, and Audio files (MP3, WAV, M4A, AAC, OGG,
              FLAC, WEBM). Maximum file size: {maxFileSize}MB
            </p>
          </div>
        </Dragger>

        {uploadProgress && (
          <Card size='small' style={{ background: '#f9f9f9' }}>
            <Space direction='vertical' size='middle' style={{ width: '100%' }}>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                }}
              >
                <Space>
                  {getFileIcon(uploadProgress.fileName)}
                  <Text strong>{uploadProgress.fileName}</Text>
                </Space>
                {getProgressIcon(uploadProgress.status)}
              </div>

              <Progress
                percent={uploadProgress.percent}
                status={
                  uploadProgress.status === 'error' ? 'exception' : 'active'
                }
                strokeColor={{
                  '0%': '#108ee9',
                  '100%': '#87d068',
                }}
                trailColor='#f0f0f0'
                showInfo={true}
              />

              <div>
                {uploadProgress.status === 'uploading' && (
                  <Alert
                    message='Processing Upload'
                    description='Your file is being uploaded and will be processed automatically.'
                    type='info'
                    showIcon
                    icon={<LoadingOutlined />}
                    style={{ padding: '8px 12px' }}
                  />
                )}

                {uploadProgress.status === 'done' && (
                  <Alert
                    message='Upload Complete'
                    description='File uploaded successfully! Processing will continue in the background.'
                    type='success'
                    showIcon
                    icon={<CheckCircleOutlined />}
                    style={{ padding: '8px 12px' }}
                  />
                )}

                {uploadProgress.status === 'error' && (
                  <Alert
                    message='Upload Failed'
                    description='There was an error uploading your file. Please try again.'
                    type='error'
                    showIcon
                    icon={<CloseCircleOutlined />}
                    style={{ padding: '8px 12px' }}
                    action={
                      <Button
                        size='small'
                        type='primary'
                        onClick={() => setUploadProgress(null)}
                      >
                        Try Again
                      </Button>
                    }
                  />
                )}
              </div>
            </Space>
          </Card>
        )}
      </Space>

      <div style={{ marginTop: '16px' }}>
        <Paragraph type='secondary' style={{ fontSize: '12px' }}>
          <strong>Supported formats:</strong>
          <br />
          • PDF documents (.pdf)
          <br />
          • Plain text files (.txt)
          <br />
          • Audio files (.mp3, .wav, .m4a, .aac, .ogg, .flac, .webm)
          <br />
          <br />
          Files will be processed automatically after upload. Audio files will
          be transcribed to text and then processed into searchable chunks for
          the knowledge base.
        </Paragraph>
      </div>
    </Card>
  );
};

export default SourceUploader;
