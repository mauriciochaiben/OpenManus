import type { ChatMessage } from '../../../types';
import { createNote } from '../../notes/services/notesApi';
import type { NoteCreate } from '../../notes/types';

/**
 * Copy text to clipboard
 */
export const copyToClipboard = async (text: string): Promise<void> => {
    try {
        if (navigator.clipboard && window.isSecureContext) {
            // Use modern clipboard API if available
            await navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers or non-secure contexts
            const textArea = document.createElement('textarea');
            textArea.value = text;
            textArea.style.position = 'fixed';
            textArea.style.left = '-999999px';
            textArea.style.top = '-999999px';
            document.body.appendChild(textArea);
            textArea.focus();
            textArea.select();

            try {
                document.execCommand('copy');
            } catch (err) {
                throw new Error('Failed to copy text');
            } finally {
                document.body.removeChild(textArea);
            }
        }
    } catch (error) {
        console.error('Error copying to clipboard:', error);
        throw error;
    }
};

/**
 * Save a chat message as a note
 */
export const saveMessageAsNote = async (message: ChatMessage): Promise<void> => {
    try {
        // Generate a meaningful title from the message content
        const title = generateNoteTitle(message.content);

        // Prepare note data
        const noteData: NoteCreate = {
            title,
            content: formatMessageAsNote(message),
            tags: ['chat', 'ai-response'],
            is_public: false,
            metadata: {
                source_type: 'chat_message',
                message_id: message.id,
                message_role: message.role,
                message_timestamp: message.timestamp,
                task_id: message.task_id || null
            }
        };

        // Create the note
        await createNote(noteData);
    } catch (error) {
        console.error('Error saving message as note:', error);
        throw error;
    }
};

/**
 * Generate a meaningful title from message content
 */
const generateNoteTitle = (content: string): string => {
    // Clean the content and get first line or meaningful chunk
    const cleaned = content.trim();
    const lines = cleaned.split('\n').filter(line => line.trim());

    if (lines.length === 0) {
        return 'Chat Message Note';
    }

    const firstLine = lines[0].trim();

    // If first line is very short, try to combine with next line
    if (firstLine.length < 20 && lines.length > 1) {
        const combined = `${firstLine} ${lines[1].trim()}`;
        return truncateTitle(combined);
    }

    return truncateTitle(firstLine);
};

/**
 * Truncate title to appropriate length
 */
const truncateTitle = (title: string): string => {
    const maxLength = 80;

    if (title.length <= maxLength) {
        return title;
    }

    // Try to truncate at word boundary
    const truncated = title.substring(0, maxLength);
    const lastSpace = truncated.lastIndexOf(' ');

    if (lastSpace > maxLength * 0.7) {
        return truncated.substring(0, lastSpace) + '...';
    }

    return truncated + '...';
};

/**
 * Format chat message as note content
 */
const formatMessageAsNote = (message: ChatMessage): string => {
    const timestamp = new Date(message.timestamp).toLocaleString();
    const role = message.role === 'user' ? 'User' : 'AI Assistant';

    let content = `# Chat Message - ${role}\n\n`;
    content += `**Timestamp:** ${timestamp}\n`;

    if (message.task_id) {
        content += `**Task ID:** ${message.task_id}\n`;
    }

    content += `**Role:** ${role}\n\n`;
    content += `---\n\n`;
    content += message.content;

    return content;
};

/**
 * Format timestamp for display
 */
export const formatTime = (timestamp: string): string => {
    return new Date(timestamp).toLocaleTimeString('pt-BR', {
        hour: '2-digit',
        minute: '2-digit'
    });
};

/**
 * Format timestamp with date for notes
 */
export const formatDateTime = (timestamp: string): string => {
    return new Date(timestamp).toLocaleString('pt-BR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
};
