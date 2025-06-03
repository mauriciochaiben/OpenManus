/**
 * LLM Provider Card Component
 * Displays provider information with Flowith-inspired design
 */

import React from 'react';
import {
  Card,
  Space,
  Typography,
  Tag,
  Button,
  Avatar,
  Tooltip,
  Badge,
  Divider,
} from 'antd';
import {
  ApiOutlined,
  GlobalOutlined,
  LockOutlined,
  ToolOutlined,
  EyeOutlined,
} from '@ant-design/icons';

import { LLMProvider } from '../types';

const { Text, Title } = Typography;

interface LLMProviderCardProps {
  provider: LLMProvider;
  onSelect?: (provider: LLMProvider) => void;
  onViewModels?: (provider: LLMProvider) => void;
  selected?: boolean;
  compact?: boolean;
}

const LLMProviderCard: React.FC<LLMProviderCardProps> = ({
  provider,
  onSelect,
  onViewModels,
  selected = false,
  compact = false,
}) => {
  const getProviderIcon = (type: string) => {
    switch (type) {
      case 'openai':
        return '🤖';
      case 'anthropic':
        return '🧠';
      case 'google':
        return '🔍';
      case 'ollama':
        return '🦙';
      default:
        return '⚡';
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'openai':
        return 'blue';
      case 'anthropic':
        return 'purple';
      case 'google':
        return 'orange';
      case 'ollama':
        return 'green';
      default:
        return 'default';
    }
  };

  const renderFeatures = (features: string[], maxShow = 3) => {
    const displayFeatures = features.slice(0, maxShow);
    const remaining = features.length - maxShow;

    return (
      <Space wrap size='small'>
        {displayFeatures.map((feature) => (
          <Tag
            key={feature}
            color='blue'
            style={{ margin: '2px', fontSize: '11px' }}
          >
            {feature.replace(/_/g, ' ')}
          </Tag>
        ))}
        {remaining > 0 && (
          <Tag style={{ margin: '2px', fontSize: '11px' }}>
            +{remaining} more
          </Tag>
        )}
      </Space>
    );
  };

  if (compact) {
    return (
      <Card
        size='small'
        hoverable
        onClick={() => onSelect?.(provider)}
        style={{
          border: selected ? '2px solid #1890ff' : '1px solid #d9d9d9',
          cursor: onSelect ? 'pointer' : 'default',
        }}
      >
        <Space>
          <Avatar
            size='small'
            style={{ backgroundColor: '#f0f0f0' }}
            icon={
              <span style={{ fontSize: '16px' }}>
                {getProviderIcon(provider.type)}
              </span>
            }
          />
          <div>
            <Text strong style={{ fontSize: '14px' }}>
              {provider.displayName}
            </Text>
            <div>
              <Tag color={getTypeColor(provider.type)}>
                {provider.type.toUpperCase()}
              </Tag>
              <Text type='secondary' style={{ fontSize: '12px' }}>
                {provider.models.length} models
              </Text>
            </div>
          </div>
        </Space>
      </Card>
    );
  }

  return (
    <Card
      hoverable={!!onSelect}
      onClick={() => onSelect?.(provider)}
      style={{
        border: selected ? '2px solid #1890ff' : '1px solid #d9d9d9',
        cursor: onSelect ? 'pointer' : 'default',
        height: '100%',
      }}
      actions={[
        <Button
          key='view'
          type='text'
          icon={<EyeOutlined />}
          onClick={(e) => {
            e.stopPropagation();
            onViewModels?.(provider);
          }}
        >
          View Models
        </Button>,
        <Button
          key='select'
          type={selected ? 'primary' : 'default'}
          onClick={(e) => {
            e.stopPropagation();
            onSelect?.(provider);
          }}
        >
          {selected ? 'Selected' : 'Select'}
        </Button>,
      ]}
    >
      <Space direction='vertical' size='middle' style={{ width: '100%' }}>
        {/* Header */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
          }}
        >
          <Space>
            <Avatar
              size={48}
              style={{ backgroundColor: '#f0f0f0' }}
              icon={
                <span style={{ fontSize: '24px' }}>
                  {getProviderIcon(provider.type)}
                </span>
              }
            />
            <div>
              <Title level={5} style={{ margin: 0 }}>
                {provider.displayName}
              </Title>
              <Space size='small'>
                <Tag color={getTypeColor(provider.type)}>
                  {provider.type.toUpperCase()}
                </Tag>
                {provider.requiresApiKey ? (
                  <Tooltip title='Requires API Key'>
                    <LockOutlined style={{ color: '#faad14' }} />
                  </Tooltip>
                ) : (
                  <Tooltip title='No API Key Required'>
                    <GlobalOutlined style={{ color: '#52c41a' }} />
                  </Tooltip>
                )}
              </Space>
            </div>
          </Space>

          {selected && <Badge status='processing' text='Selected' />}
        </div>

        {/* Description */}
        <Text type='secondary' style={{ fontSize: '13px', lineHeight: '1.4' }}>
          {provider.description}
        </Text>

        <Divider style={{ margin: '8px 0' }} />

        {/* Models Count */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <Space size='large'>
            <Tooltip title='Available Models'>
              <Space size='small'>
                <ApiOutlined style={{ color: '#1890ff' }} />
                <Text strong>{provider.models.length}</Text>
                <Text type='secondary' style={{ fontSize: '12px' }}>
                  models
                </Text>
              </Space>
            </Tooltip>

            {provider.baseUrl && (
              <Tooltip title='Custom Endpoint Available'>
                <Space size='small'>
                  <ToolOutlined style={{ color: '#52c41a' }} />
                  <Text type='secondary' style={{ fontSize: '12px' }}>
                    Custom URL
                  </Text>
                </Space>
              </Tooltip>
            )}
          </Space>
        </div>

        {/* Supported Features */}
        {provider.supportedFeatures.length > 0 && (
          <div>
            <Text
              style={{
                fontSize: '12px',
                color: '#8c8c8c',
                marginBottom: '4px',
                display: 'block',
              }}
            >
              Supported Features:
            </Text>
            {renderFeatures(provider.supportedFeatures)}
          </div>
        )}

        {/* Model Preview */}
        {provider.models.length > 0 && (
          <div>
            <Text
              style={{
                fontSize: '12px',
                color: '#8c8c8c',
                marginBottom: '4px',
                display: 'block',
              }}
            >
              Popular Models:
            </Text>
            <Space wrap size='small'>
              {provider.models.slice(0, 3).map((model) => (
                <Tag
                  key={model.id}
                  style={{
                    margin: '2px',
                    fontSize: '11px',
                    backgroundColor: '#f0f9ff',
                    borderColor: '#91d5ff',
                  }}
                >
                  {model.displayName}
                </Tag>
              ))}
              {provider.models.length > 3 && (
                <Text type='secondary' style={{ fontSize: '11px' }}>
                  +{provider.models.length - 3} more
                </Text>
              )}
            </Space>
          </div>
        )}
      </Space>
    </Card>
  );
};

export default LLMProviderCard;
