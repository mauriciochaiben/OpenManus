import React, { useState, useEffect } from 'react';
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
  Popconfirm,
  message,
} from 'antd';
import {
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  SearchOutlined,
  PlusOutlined,
  BookOutlined,
  ClockCircleOutlined,
  GlobalOutlined,
  LockOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { Note, NoteSearchQuery } from '../types';
import { listNotes, searchNotes, deleteNote } from '../services/notesApi';

const { Search } = Input;
const { Option } = Select;
const { Text, Paragraph } = Typography;

interface NoteListProps {
  onCreateNote?: () => void;
  onEditNote?: (note: Note) => void;
  onViewNote?: (note: Note) => void;
  sourceId?: string;
}

const NoteList: React.FC<NoteListProps> = ({
  onCreateNote,
  onEditNote,
  onViewNote,
  sourceId,
}) => {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true); // Initial loading true for skeleton
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('updated_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Fetch notes
  const fetchNotes = async () => {
    try {
      setLoading(true);
      setError(null);

      const searchParams: NoteSearchQuery = {
        query: searchQuery || undefined,
        source_ids: sourceId ? [sourceId] : undefined,
        limit: pageSize,
        offset: (currentPage - 1) * pageSize,
        sort_by: sortBy,
        sort_order: sortOrder,
      };

      let response;
      if (searchQuery || sourceId) {
        response = await searchNotes(searchParams);
        setNotes(response.notes);
        setTotal(response.total);
      } else {
        response = await listNotes({
          limit: pageSize,
          offset: (currentPage - 1) * pageSize,
          sort_by: sortBy,
          sort_order: sortOrder,
        });
        setNotes(response.notes);
        setTotal(response.total);
      }
    } catch (error) {
      console.error('Error fetching notes:', error);
      setError('Falha ao carregar notas. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotes();
  }, [currentPage, pageSize, searchQuery, sortBy, sortOrder, sourceId]);

  // Handle delete
  const handleDelete = async (noteId: string) => {
    try {
      await deleteNote(noteId);
      message.success('Note deleted successfully');
      fetchNotes();
    } catch (error) {
      message.error('Failed to delete note');
      console.error('Error deleting note:', error);
    }
  };

  // Handle retry
  const handleRetry = () => {
    setError(null);
    fetchNotes();
  };

  // Format date
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 1) return 'Today';
    if (diffDays === 2) return 'Yesterday';
    if (diffDays <= 7) return `${diffDays} days ago`;

    return date.toLocaleDateString();
  };

  // Render note item
  const renderNoteItem = (note: Note) => (
    <List.Item
      key={note.id}
      actions={[
        <Tooltip key='view' title='View note'>
          <Button
            type='text'
            icon={<EyeOutlined />}
            onClick={() => onViewNote?.(note)}
          />
        </Tooltip>,
        <Tooltip key='edit' title='Edit note'>
          <Button
            type='text'
            icon={<EditOutlined />}
            onClick={() => onEditNote?.(note)}
          />
        </Tooltip>,
        <Popconfirm
          key='delete'
          title='Are you sure you want to delete this note?'
          onConfirm={() => handleDelete(note.id)}
          okText='Yes'
          cancelText='No'
        >
          <Tooltip title='Delete note'>
            <Button type='text' icon={<DeleteOutlined />} danger />
          </Tooltip>
        </Popconfirm>,
      ]}
    >
      <List.Item.Meta
        avatar={
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '8px',
              backgroundColor: '#f0f0f0',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <BookOutlined style={{ fontSize: '18px', color: '#1890ff' }} />
          </div>
        }
        title={
          <Space style={{ width: '100%', justifyContent: 'space-between' }}>
            <Text
              strong
              style={{ cursor: 'pointer' }}
              onClick={() => onViewNote?.(note)}
            >
              {note.title}
            </Text>
            <Space>
              {note.is_public ? (
                <Tooltip title='Public note'>
                  <GlobalOutlined style={{ color: '#52c41a' }} />
                </Tooltip>
              ) : (
                <Tooltip title='Private note'>
                  <LockOutlined style={{ color: '#999' }} />
                </Tooltip>
              )}
            </Space>
          </Space>
        }
        description={
          <Space direction='vertical' style={{ width: '100%' }} size='small'>
            {/* Content preview */}
            <Paragraph
              ellipsis={{ rows: 2, expandable: false }}
              style={{ margin: 0, color: '#666' }}
            >
              {note.content}
            </Paragraph>

            {/* Tags */}
            {note.tags && note.tags.length > 0 && (
              <Space wrap size={[4, 4]}>
                {note.tags.map((tag) => (
                  <Tag key={tag} color='blue'>
                    {tag}
                  </Tag>
                ))}
              </Space>
            )}

            {/* Metadata */}
            <Space wrap style={{ marginTop: '8px' }}>
              <Space size='small'>
                <ClockCircleOutlined style={{ color: '#999' }} />
                <Text type='secondary' style={{ fontSize: '12px' }}>
                  Updated {formatDate(note.updated_at)}
                </Text>
              </Space>

              {note.word_count && (
                <Text type='secondary' style={{ fontSize: '12px' }}>
                  {note.word_count} words
                </Text>
              )}

              {note.reading_time && (
                <Text type='secondary' style={{ fontSize: '12px' }}>
                  {note.reading_time} read
                </Text>
              )}

              {note.source_count && note.source_count > 0 && (
                <Text type='secondary' style={{ fontSize: '12px' }}>
                  {note.source_count} source{note.source_count > 1 ? 's' : ''}
                </Text>
              )}
            </Space>
          </Space>
        }
      />
    </List.Item>
  );

  // Show error state
  if (error) {
    return (
      <Card>
        <Space direction='vertical' style={{ width: '100%' }} size='large'>
          {/* Header */}
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <Space>
              <BookOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
              <Typography.Title level={4} style={{ margin: 0 }}>
                Notes
              </Typography.Title>
            </Space>
            {onCreateNote && (
              <Button
                type='primary'
                icon={<PlusOutlined />}
                onClick={onCreateNote}
                disabled
              >
                Create Note
              </Button>
            )}
          </div>

          {/* Controls */}
          <Space style={{ width: '100%' }}>
            <Search
              placeholder='Search notes...'
              allowClear
              disabled
              style={{ width: 300 }}
              enterButton={<SearchOutlined />}
            />

            <Select
              placeholder='Sort by'
              value={`${sortBy}-${sortOrder}`}
              disabled
              style={{ width: 150 }}
            >
              <Option value='updated_at-desc'>Latest Updated</Option>
              <Option value='updated_at-asc'>Oldest Updated</Option>
              <Option value='created_at-desc'>Recently Created</Option>
              <Option value='created_at-asc'>Oldest Created</Option>
              <Option value='title-asc'>Title A-Z</Option>
              <Option value='title-desc'>Title Z-A</Option>
            </Select>
          </Space>

          <Result
            status='error'
            title='Erro ao carregar notas'
            subTitle={error}
            extra={[
              <Button
                key='retry'
                type='primary'
                icon={<ReloadOutlined />}
                onClick={handleRetry}
              >
                Tentar Novamente
              </Button>,
            ]}
          />
        </Space>
      </Card>
    );
  }

  return (
    <Card>
      <Space direction='vertical' style={{ width: '100%' }} size='large'>
        {/* Header */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <Space>
            <BookOutlined style={{ fontSize: '24px', color: '#1890ff' }} />
            <Typography.Title level={4} style={{ margin: 0 }}>
              Notes
            </Typography.Title>
          </Space>
          {onCreateNote && (
            <Button
              type='primary'
              icon={<PlusOutlined />}
              onClick={onCreateNote}
            >
              Create Note
            </Button>
          )}
        </div>

        {/* Controls */}
        <Space style={{ width: '100%' }}>
          <Search
            placeholder='Search notes...'
            allowClear
            onSearch={(value) => setSearchQuery(value)}
            style={{ width: 300 }}
            enterButton={<SearchOutlined />}
          />

          <Select
            placeholder='Sort by'
            value={`${sortBy}-${sortOrder}`}
            onChange={(value) => {
              const [field, order] = value.split('-');
              setSortBy(field);
              setSortOrder(order as 'asc' | 'desc');
            }}
            style={{ width: 150 }}
          >
            <Option value='updated_at-desc'>Latest Updated</Option>
            <Option value='updated_at-asc'>Oldest Updated</Option>
            <Option value='created_at-desc'>Recently Created</Option>
            <Option value='created_at-asc'>Oldest Created</Option>
            <Option value='title-asc'>Title A-Z</Option>
            <Option value='title-desc'>Title Z-A</Option>
          </Select>
        </Space>

        {/* Notes List */}
        <Spin spinning={loading}>
          {!loading && notes.length === 0 ? (
            <Empty
              description={
                searchQuery
                  ? 'Nenhuma nota encontrada com o termo pesquisado'
                  : sourceId
                    ? 'Nenhuma nota vinculada a esta fonte'
                    : 'Nenhuma nota criada ainda'
              }
              image={Empty.PRESENTED_IMAGE_SIMPLE}
            >
              {searchQuery ? (
                <Button type='primary' onClick={() => setSearchQuery('')}>
                  Limpar Busca
                </Button>
              ) : onCreateNote ? (
                <Button
                  type='primary'
                  icon={<PlusOutlined />}
                  onClick={onCreateNote}
                >
                  Criar Primeira Nota
                </Button>
              ) : null}
            </Empty>
          ) : (
            <List
              itemLayout='vertical'
              dataSource={notes}
              renderItem={renderNoteItem}
            />
          )}
        </Spin>

        {/* Pagination */}
        {total > pageSize && (
          <Pagination
            current={currentPage}
            total={total}
            pageSize={pageSize}
            onChange={(page, size) => {
              setCurrentPage(page);
              if (size !== pageSize) {
                setPageSize(size);
              }
            }}
            showSizeChanger
            showQuickJumper
            showTotal={(total, range) =>
              `${range[0]}-${range[1]} de ${total} notas`
            }
          />
        )}
      </Space>
    </Card>
  );
};

export default NoteList;
