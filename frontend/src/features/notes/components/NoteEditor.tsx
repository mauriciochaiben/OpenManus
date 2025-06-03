import React, { useState, useEffect } from 'react';
import {
  Card,
  Input,
  Button,
  Space,
  Typography,
  Switch,
  Tag,
  message,
  Spin,
  Row,
  Col,
  Divider,
} from 'antd';
import {
  SaveOutlined,
  EditOutlined,
  TagOutlined,
  GlobalOutlined,
  LockOutlined,
} from '@ant-design/icons';
import MDEditor from '@uiw/react-md-editor';
import { Note, NoteCreate, NoteUpdate } from '../types';
import { createNote, updateNote, getNote } from '../services/notesApi';
import { SourceSelector } from '../../knowledge/components';

interface NoteEditorProps {
  noteId?: string;
  initialNote?: Note;
  onSave?: (note: Note) => void;
  onCancel?: () => void;
  mode?: 'create' | 'edit' | 'view';
}

const NoteEditor: React.FC<NoteEditorProps> = ({
  noteId,
  initialNote,
  onSave,
  onCancel,
  mode: initialMode = 'create',
}) => {
  const [mode, setMode] = useState(initialMode);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [note, setNote] = useState<Partial<Note>>({
    title: '',
    content: '',
    source_ids: [],
    tags: [],
    is_public: false,
    ...initialNote,
  });
  const [newTag, setNewTag] = useState('');

  // Load note if noteId is provided
  useEffect(() => {
    if (noteId && !initialNote) {
      loadNote();
    }
  }, [noteId]);

  const loadNote = async () => {
    if (!noteId) return;

    try {
      setLoading(true);
      const loadedNote = await getNote(noteId);
      setNote(loadedNote);
    } catch (error) {
      message.error('Failed to load note');
      console.error('Error loading note:', error);
    } finally {
      setLoading(false);
    }
  };

  // Handle save
  const handleSave = async () => {
    if (!note.title?.trim()) {
      message.error('Please enter a note title');
      return;
    }

    if (!note.content?.trim()) {
      message.error('Please enter note content');
      return;
    }

    try {
      setSaving(true);
      let savedNote: Note;

      if (noteId && mode === 'edit') {
        // Update existing note
        const updateData: NoteUpdate = {
          title: note.title,
          content: note.content,
          source_ids: note.source_ids,
          tags: note.tags,
          is_public: note.is_public,
          metadata: note.metadata,
        };
        savedNote = await updateNote(noteId, updateData);
      } else {
        // Create new note
        const createData: NoteCreate = {
          title: note.title!,
          content: note.content!,
          source_ids: note.source_ids,
          tags: note.tags,
          is_public: note.is_public,
          metadata: note.metadata,
        };
        savedNote = await createNote(createData);
      }

      message.success(`Note ${noteId ? 'updated' : 'created'} successfully`);
      setNote(savedNote);
      onSave?.(savedNote);
      setMode('view');
    } catch (error) {
      message.error(`Failed to ${noteId ? 'update' : 'create'} note`);
      console.error('Error saving note:', error);
    } finally {
      setSaving(false);
    }
  };

  // Handle tag operations
  const addTag = () => {
    if (newTag.trim() && !note.tags?.includes(newTag.trim().toLowerCase())) {
      setNote((prev) => ({
        ...prev,
        tags: [...(prev.tags || []), newTag.trim().toLowerCase()],
      }));
      setNewTag('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setNote((prev) => ({
      ...prev,
      tags: prev.tags?.filter((tag) => tag !== tagToRemove) || [],
    }));
  };

  if (loading) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: '40px' }}>
          <Spin size='large' />
        </div>
      </Card>
    );
  }

  return (
    <Card
      title={
        <Space>
          <EditOutlined />
          <span>
            {mode === 'create'
              ? 'New Note'
              : mode === 'edit'
                ? 'Edit Note'
                : 'View Note'}
          </span>
          {note.is_public ? (
            <GlobalOutlined style={{ color: '#52c41a' }} />
          ) : (
            <LockOutlined style={{ color: '#faad14' }} />
          )}
        </Space>
      }
      extra={
        <Space>
          {mode === 'view' && (
            <Button icon={<EditOutlined />} onClick={() => setMode('edit')}>
              Edit
            </Button>
          )}
          {(mode === 'edit' || mode === 'create') && (
            <>
              <Button onClick={onCancel}>Cancel</Button>
              <Button
                type='primary'
                icon={<SaveOutlined />}
                loading={saving}
                onClick={handleSave}
              >
                Save
              </Button>
            </>
          )}
        </Space>
      }
    >
      <Space direction='vertical' size='large' style={{ width: '100%' }}>
        {/* Title */}
        <div>
          <Typography.Text strong>Title</Typography.Text>
          <Input
            value={note.title}
            onChange={(e) =>
              setNote((prev) => ({ ...prev, title: e.target.value }))
            }
            placeholder='Enter note title...'
            disabled={mode === 'view'}
            style={{ marginTop: '8px' }}
            size='large'
          />
        </div>

        {/* Settings Row */}
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12}>
            <Space>
              <Typography.Text strong>Public:</Typography.Text>
              <Switch
                checked={note.is_public}
                onChange={(checked) =>
                  setNote((prev) => ({ ...prev, is_public: checked }))
                }
                disabled={mode === 'view'}
                checkedChildren='Public'
                unCheckedChildren='Private'
              />
            </Space>
          </Col>
        </Row>

        {/* Tags */}
        <div>
          <Typography.Text strong>Tags</Typography.Text>
          <div style={{ marginTop: '8px' }}>
            <Space wrap>
              {note.tags?.map((tag) => (
                <Tag
                  key={tag}
                  closable={mode !== 'view'}
                  onClose={() => removeTag(tag)}
                  icon={<TagOutlined />}
                >
                  {tag}
                </Tag>
              ))}
            </Space>
            {mode !== 'view' && (
              <div style={{ marginTop: '8px' }}>
                <Input
                  value={newTag}
                  onChange={(e) => setNewTag(e.target.value)}
                  onPressEnter={addTag}
                  placeholder='Add a tag...'
                  style={{ width: '200px' }}
                  addonAfter={
                    <Button
                      type='text'
                      onClick={addTag}
                      disabled={!newTag.trim()}
                    >
                      Add
                    </Button>
                  }
                />
              </div>
            )}
          </div>
        </div>

        {/* Knowledge Sources */}
        <div>
          <Typography.Text strong>Knowledge Sources</Typography.Text>
          <div style={{ marginTop: '8px' }}>
            <SourceSelector
              selectedSourceIds={note.source_ids || []}
              onSelectionChange={(sourceIds) =>
                setNote((prev) => ({ ...prev, source_ids: sourceIds }))
              }
              disabled={mode === 'view'}
              showCard={false}
              placeholder='Link knowledge sources to this note'
            />
          </div>
        </div>

        <Divider />

        {/* Content Editor */}
        <div>
          <Typography.Text strong>Content</Typography.Text>
          <div style={{ marginTop: '8px' }}>
            {mode === 'view' ? (
              <MDEditor.Markdown
                source={note.content || ''}
                style={{
                  padding: '16px',
                  border: '1px solid #d9d9d9',
                  borderRadius: '6px',
                }}
              />
            ) : (
              <MDEditor
                value={note.content || ''}
                onChange={(val) =>
                  setNote((prev) => ({ ...prev, content: val || '' }))
                }
                preview='edit'
                height={400}
                data-color-mode='light'
              />
            )}
          </div>
        </div>

        {/* Metadata */}
        {note.word_count && (
          <Space>
            <Typography.Text type='secondary'>
              {note.word_count} words
            </Typography.Text>
            {note.reading_time && (
              <Typography.Text type='secondary'>
                • {note.reading_time}
              </Typography.Text>
            )}
          </Space>
        )}
      </Space>
    </Card>
  );
};

export default NoteEditor;
