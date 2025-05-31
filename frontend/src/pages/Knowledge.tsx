import React, { useState } from 'react';
import {
    Layout,
    Row,
    Col,
    Space,
    Typography,
    Divider,
    Card,
    Statistic,
    Alert,
    Badge
} from 'antd';
import {
    BookOutlined,
    CloudUploadOutlined,
    FileTextOutlined,
    DatabaseOutlined
} from '@ant-design/icons';
import { SourceUploader, SourceList } from '../features/knowledge/components';
import type { UploadSourceResponse } from '../features/knowledge/types';

const { Content } = Layout;
const { Title, Paragraph, Text } = Typography;

const Knowledge: React.FC = () => {
    const [refreshTrigger, setRefreshTrigger] = useState(0);
    const [uploadStats, setUploadStats] = useState({
        totalUploads: 0,
        processingCount: 0,
        completedCount: 0,
        failedCount: 0
    });

    // Handle successful upload to refresh the source list
    const handleUploadSuccess = (response: UploadSourceResponse) => {
        console.log('Upload successful:', response);
        // Trigger refresh of the source list
        setRefreshTrigger(prev => prev + 1);
        // Update upload stats
        setUploadStats(prev => ({
            ...prev,
            totalUploads: prev.totalUploads + 1,
            processingCount: prev.processingCount + 1
        }));
    };

    // Handle source deletion to refresh stats if needed
    const handleSourceDeleted = (sourceId: string) => {
        console.log('Source deleted:', sourceId);
        setRefreshTrigger(prev => prev + 1);
    };

    // Handle upload error
    const handleUploadError = (error: any) => {
        console.error('Upload error:', error);
    };

    return (
        <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
            <Content style={{ padding: '24px' }}>
                <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
                    {/* Page Header */}
                    <div style={{ marginBottom: '32px' }}>
                        <Space align="center" style={{ marginBottom: '16px' }}>
                            <BookOutlined style={{ fontSize: '32px', color: '#1890ff' }} />
                            <Title level={2} style={{ margin: 0 }}>
                                Knowledge Management
                            </Title>
                        </Space>

                        <Paragraph style={{ fontSize: '16px', color: '#666', marginBottom: '24px' }}>
                            Upload and manage your knowledge sources. Transform documents into searchable content
                            for enhanced AI assistance and information retrieval.
                        </Paragraph>

                        {/* Quick Stats */}
                        <Row gutter={[16, 16]}>
                            <Col xs={12} sm={6}>
                                <Card size="small">
                                    <Statistic
                                        title="Total Sources"
                                        value={uploadStats.totalUploads}
                                        prefix={<DatabaseOutlined />}
                                        valueStyle={{ color: '#1890ff' }}
                                    />
                                </Card>
                            </Col>
                            <Col xs={12} sm={6}>
                                <Card size="small">
                                    <Statistic
                                        title="Processing"
                                        value={uploadStats.processingCount}
                                        prefix={<Badge status="processing" />}
                                        valueStyle={{ color: '#faad14' }}
                                    />
                                </Card>
                            </Col>
                            <Col xs={12} sm={6}>
                                <Card size="small">
                                    <Statistic
                                        title="Completed"
                                        value={uploadStats.completedCount}
                                        prefix={<Badge status="success" />}
                                        valueStyle={{ color: '#52c41a' }}
                                    />
                                </Card>
                            </Col>
                            <Col xs={12} sm={6}>
                                <Card size="small">
                                    <Statistic
                                        title="Failed"
                                        value={uploadStats.failedCount}
                                        prefix={<Badge status="error" />}
                                        valueStyle={{ color: '#ff4d4f' }}
                                    />
                                </Card>
                            </Col>
                        </Row>
                    </div>

                    {/* Upload Section */}
                    <Row gutter={[24, 24]} style={{ marginBottom: '32px' }}>
                        <Col xs={24} lg={14}>
                            <SourceUploader
                                onUploadSuccess={handleUploadSuccess}
                                onUploadError={handleUploadError}
                                maxFileSize={50}
                            />
                        </Col>

                        <Col xs={24} lg={10}>
                            <Card
                                title={
                                    <Space>
                                        <CloudUploadOutlined />
                                        <span>Upload Guidelines</span>
                                    </Space>
                                }
                                style={{ height: '100%' }}
                            >
                                <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                                    <Alert
                                        message="Supported File Types"
                                        description={
                                            <Space direction="vertical" size="small">
                                                <Space>
                                                    <FileTextOutlined style={{ color: '#1890ff' }} />
                                                    <Text>Plain Text Files (.txt)</Text>
                                                </Space>
                                                <Space>
                                                    <FileTextOutlined style={{ color: '#ff4d4f' }} />
                                                    <Text>PDF Documents (.pdf)</Text>
                                                </Space>
                                            </Space>
                                        }
                                        type="info"
                                        showIcon
                                    />

                                    <div>
                                        <Title level={5}>Processing Information</Title>
                                        <ul style={{ margin: 0, paddingLeft: '20px' }}>
                                            <li>Maximum file size: <Text strong>50MB</Text></li>
                                            <li>Files are automatically processed into searchable chunks</li>
                                            <li>Processing time varies by file size and complexity</li>
                                            <li>Monitor progress in real-time below</li>
                                            <li>Failed uploads can be retried automatically</li>
                                        </ul>
                                    </div>

                                    <Alert
                                        message="Pro Tip"
                                        description="For best results, ensure your documents have clear text content. Scanned PDFs may require OCR processing."
                                        type="success"
                                        showIcon
                                    />
                                </Space>
                            </Card>
                        </Col>
                    </Row>

                    <Divider orientation="left">
                        <Space>
                            <DatabaseOutlined />
                            <span>Source Management</span>
                        </Space>
                    </Divider>

                    {/* Sources List Section */}
                    <SourceList
                        refreshTrigger={refreshTrigger}
                        onSourceDeleted={handleSourceDeleted}
                        enablePolling={true}
                        pollingInterval={5000}
                    />
                </div>
            </Content>
        </Layout>
    );
};

export default Knowledge;
