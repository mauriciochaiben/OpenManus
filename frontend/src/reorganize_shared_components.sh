#!/bin/bash

echo "🔧 Reorganizando componentes compartilhados do frontend..."
echo "========================================================="

# Criar diretórios compartilhados se não existirem
echo "📁 Criando estrutura de diretórios compartilhados..."
mkdir -p frontend/src/shared/components
mkdir -p frontend/src/shared/hooks
mkdir -p frontend/src/shared/utils
mkdir -p frontend/src/shared/services

echo ""
echo "🎯 UTILS COMPARTILHADOS:"
echo "------------------------"

# 1. Extrair copyToClipboard para utils compartilhados
echo "📦 Extraindo função copyToClipboard..."
cat > frontend/src/shared/utils/clipboard.ts << 'EOF'
/**
 * Clipboard utilities shared across features
 */

/**
 * Copy text to clipboard with fallback for older browsers
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
 * Check if clipboard API is available
 */
export const isClipboardSupported = (): boolean => {
  return !!(navigator.clipboard && window.isSecureContext);
};
EOF

# 2. Extrair formatters comuns
echo "📦 Criando formatters compartilhados..."
cat > frontend/src/shared/utils/formatters.ts << 'EOF'
/**
 * Common formatting utilities
 */

/**
 * Format date to locale string
 */
export const formatDate = (date: string | Date): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString();
};

/**
 * Format date with time
 */
export const formatDateTime = (date: string | Date): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleString();
};

/**
 * Generate a title from text content (first 50 chars)
 */
export const generateTitle = (content: string, maxLength: number = 50): string => {
  const sanitized = content.replace(/[#*\n\r]/g, '').trim();
  return sanitized.length > maxLength
    ? sanitized.substring(0, maxLength) + '...'
    : sanitized || 'Untitled';
};

/**
 * Truncate text with ellipsis
 */
export const truncateText = (text: string, maxLength: number): string => {
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
};
EOF

# 3. Criar validation utils
echo "📦 Criando validation utils..."
cat > frontend/src/shared/utils/validation.ts << 'EOF'
/**
 * Common validation utilities
 */

/**
 * Check if string is not empty
 */
export const isNotEmpty = (value: string): boolean => {
  return value.trim().length > 0;
};

/**
 * Validate email format
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Check if URL is valid
 */
export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

/**
 * Validate file extension
 */
export const hasValidExtension = (filename: string, allowedExtensions: string[]): boolean => {
  const extension = filename.split('.').pop()?.toLowerCase();
  return extension ? allowedExtensions.includes(extension) : false;
};
EOF

# 4. Atualizar index dos utils compartilhados
echo "📝 Atualizando exports dos utils compartilhados..."
cat > frontend/src/shared/utils/index.ts << 'EOF'
// Shared utilities exports
export * from './clipboard';
export * from './formatters';
export * from './validation';
EOF

echo ""
echo "🎯 HOOKS COMPARTILHADOS:"
echo "------------------------"

# 5. Verificar se useWebSocket já está na localização correta
if [ -f "frontend/src/hooks/useWebSocket.ts" ]; then
    echo "✅ useWebSocket já está localizado corretamente em hooks globais"
else
    echo "⚠️  useWebSocket não encontrado na localização esperada"
fi

echo ""
echo "🎯 COMPONENTS POTENCIALMENTE COMPARTILHADOS:"
echo "--------------------------------------------"

echo "📦 Os seguintes componentes podem se beneficiar de centralização:"
echo "• SourceSelector (knowledge) - usado por notes"
echo "• MessageList/MessageItem (chat) - padrão reutilizável"
echo "• WorkflowProgress (workflow) - pode ser genérico"

echo ""
echo "⚠️  IMPORTANTE - COMANDOS GIT MV MANUAIS NECESSÁRIOS:"
echo "===================================================="

echo ""
echo "1️⃣ ATUALIZAR IMPORTS EM CHAT UTILS:"
echo "Editar frontend/src/features/chat/utils/messageActions.ts"
echo "Substituir a função copyToClipboard por:"
echo "import { copyToClipboard } from '../../../shared/utils/clipboard';"

echo ""
echo "2️⃣ MOVER COMPONENTE SOURCESELECTOR (opcional):"
echo "Para reutilização entre knowledge e notes:"
echo "git mv frontend/src/features/knowledge/components/SourceSelector.tsx frontend/src/shared/components/"
echo "Atualizar imports em:"
echo "• frontend/src/features/knowledge/components/index.ts"
echo "• frontend/src/features/notes/components/NoteEditor.tsx"

echo ""
echo "3️⃣ ATUALIZAR IMPORTS GLOBAIS:"
echo "Adicionar ao frontend/src/shared/index.ts:"
echo "export * from './utils';"
echo "export * from './components';"
echo "export * from './hooks';"

echo ""
echo "✅ Estrutura de utils compartilhados criada!"
echo "📋 Próximos passos:"
echo "• Atualizar imports nas features que usam essas funções"
echo "• Considerar mover componentes reutilizáveis para shared/"
echo "• Implementar testes para utils compartilhados"
