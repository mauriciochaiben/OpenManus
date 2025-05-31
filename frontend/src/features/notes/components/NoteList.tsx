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
    message,
    Popconfirm,
    Tooltip
} from 'antd';
import {
    EditOutlined,
    DeleteOutlined,
    EyeOutlined,
    SearchOutlined,
    PlusOutlined,
    BookOutlined,
    ClockCircleOutlined,
    UserOutlined,
    GlobalOutlined,
    LockOutlined
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
    showSourceFilter?: boolean;
    sourceId?: string;
}

const NoteList: React.FC<NoteListProps> = ({
    onCreateNote,
    onEditNote,
    onViewNote,
    showSourceFilter = false,
    sourceId
}) => {
    const [notes, setNotes] = useState<Note[]>([]);
    const [loading, setLoading] = useState(false);
    const [total, setTotal] = useState(0);
    const [currentPage, setCurrentPage] = useState(1);
    const [pageSize, setPageSize] = useState(10);
    const [searchQuery, setSearchQuery] = useState('');
    const [sortBy, setSortBy] = useState('updated_at');
    const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
    const [selectedTags, setSelectedTags] = useState<string[]>([]);

    // Fetch notes
    const fetchNotes = async () => {
        try {
            setLoading(true);

            const searchParams: NoteSearchQuery = {
                query: searchQuery || undefined,
                tags: selectedTags.length > 0 ? selectedTags : undefined,
                source_ids: sourceId ? [sourceId] : undefined,
                limit: pageSize,
                offset: (currentPage - 1) * pageSize,
                sort_by: sortBy,
                sort_order: sortOrder
            };

            let response;
            if (searchQuery || selectedTags.length > 0 || sourceId) {
                response = await searchNotes(searchParams);
                setNotes(response.notes);
                setTotal(response.total);
            } else {
                response = await listNotes({
                    limit: pageSize,
                    offset: (currentPage - 1) * pageSize,
                    sort_by: sortBy,
                    sort_order: sortOrder
                });
                setNotes(response.notes);
                setTotal(response.total);
            }
        } catch (error) {
            message.error('Failed to load notes');
            console.error('Error fetching notes:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchNotes();
    }, [currentPage, pageSize, sortBy, sortOrder]);

    // Handle search
    const handleSearch = (value: string) => {
        setSearchQuery(value);
        setCurrentPage(1);
        fetchNotes();
    };

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

    // Format date
    const formatDate = (dateString: string) => {
        return new Date(dateString).toLocaleDateString();
    };

    // Render note item
    const renderNoteItem = (note: Note) => (
        <List.Item
            key={note.id}
            actions={[
                <Tooltip title="View note">
                    <Button
                        type="text"
                        icon={<EyeOutlined />}
                        onClick={() => onViewNote?.(note)}
                    />
                </Tooltip>,
                <Tooltip title="Edit note">
                    <Button
                        type="text"
                        icon={<EditOutlined />}
                        onClick={() => onEditNote?.(note)}
                    />
                </Tooltip>,
                <Popconfirm
                    title="Delete this note?"
                    description="This action cannot be undone."
                    onConfirm={() => handleDelete(note.id)}
                    okText="Delete"
                    cancelText="Cancel"
                    okType="danger"
                >
                    <Tooltip title="Delete note">
                        <Button
                            type="text"
                            danger
                            icon={<DeleteOutlined />}
                        />
                    </Tooltip>
                </Popconfirm>
            ]}
        >
            <List.Item.Meta
                title={
                    <Space>
                        <span>{note.title}</span>
                        {note.is_public ? (
                            <Tooltip title="Public note">
                                <GlobalOutlined style={{ color: '#52c41a' }} />
                            </Tooltip>
                        ) : (
                            <Tooltip title="Private note">
                                <LockOutlined style={{ color: '#faad14' }} />
                            </Tooltip>
                        )}
                    </Space>
                }
                description={
                    <Space direction="vertical" size="small">
                        <Paragraph
                            ellipsis={{ rows: 2, expandable: false }}
                            style={{ margin: 0, color: '#666' }}
                        >
                            {note.content.replace(/[#*_`]/g, '').substring(0, 150)}
                        </Paragraph>

                        <Space wrap>
                            {note.tags?.map(tag => (
                                <Tag key={tag} size="small" color="blue">
                                    {tag}
                                </Tag>
                            ))}
                        </Space>

                        <Space size="large">
                            <Space size="small">
                                <ClockCircleOutlined />
                                <Text type="secondary" style={{ fontSize: '12px' }}>
                                    {formatDate(note.updated_at)}
                                </Text>
                            </Space>

                            {note.reading_time && (
                                <Space size="small">
                                    <BookOutlined />
                                    <Text type="secondary" style={{ fontSize: '12px' }}>
                                        {note.reading_time}
                                    </Text>
                                </Space>
                            )}

                            {note.source_count && note.source_count > 0 && (
                                <Space size="small">
                                    <BookOutlined />
                                    <Text type="secondary" style={{ fontSize: '12px' }}>
                                        {note.source_count} source{note.source_count !== 1 ? 's' : ''}
                                    </Text>
                                </Space>
                            )}
                        </Space>
                    </Space>
                }
            />
        </List.Item>
    );

    return (
        <Card>
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                {/* Header */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography.Title level={4} style={{ margin: 0 }}>
                        {sourceId ? 'Related Notes' : 'Notes'}
                    </Typography.Title>
                    {onCreateNote && (
                        <Button type="primary" icon={<PlusOutlined />} onClick={onCreateNote}>
                            New Note
                        </Button>
                    )}
                </div>

                {/* Search and Filters */}
                <Space wrap>
                    <Search
                        placeholder="Search notes..."
                        allowClear
                        onSearch={handleSearch}
                        style={{ width: 300 }}
                        enterButton={<SearchOutlined />}
                    />

                    <Select
                        placeholder="Sort by"
                        value={`${sortBy}-${sortOrder}`}
                        onChange={(value) => {
                            const [field, order] = value.split('-');
                            setSortBy(field);
                            setSortOrder(order as 'asc' | 'desc');
                        }}
                        style={{ width: 150 }}
                    >
                        <Option value="updated_at-desc">Latest Updated</Option>
                        <Option value="updated_at-asc">Oldest Updated</Option>
                        <Option value="created_at-desc">Recently Created</Option>
                        <Option value="created_at-asc">Oldest Created</Option>
                        <Option value="title-asc">Title A-Z</Option>
                        <Option value="title-desc">Title Z-A</Option>
                    </Select>
                </Space>

                {/* Notes List */}
                <Spin spinning={loading}>
                    {notes.length > 0 ? (
                        <List
                            itemLayout="vertical"
                            dataSource={notes}
                            renderItem={renderNoteItem}
                        />
                    ) : (
                        <Empty
                            description={
                                searchQuery ? 'No notes found matching your search' : 'No notes yet'
                            }
                            image={Empty.PRESENTED_IMAGE_SIMPLE}
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
                            `${range[0]}-${range[1]} of ${total} notes`
                        }
                    />
                )}
            </Space>
        </Card>
    );
};

export default NoteList;
