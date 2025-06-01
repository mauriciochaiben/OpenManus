#!/bin/bash

echo "🚀 Reorganizando estrutura de features do frontend..."

# 1. Padronizar stores -> store (canvas)
echo "📁 Padronizando canvas/stores/ para canvas/store/..."
git mv canvas/stores canvas/store

# 2. Adicionar diretórios faltantes para features existentes com conteúdo

# Tasks - adicionar store e types se necessário
echo "📁 Criando diretórios faltantes para tasks..."
if [ ! -d "tasks/store" ]; then
    mkdir -p tasks/store
fi

# Notes - adicionar hooks e store se necessário  
echo "📁 Criando diretórios faltantes para notes..."
if [ ! -d "notes/hooks" ]; then
    mkdir -p notes/hooks
fi
if [ ! -d "notes/store" ]; then
    mkdir -p notes/store
fi

# Workflow - adicionar estrutura completa
echo "📁 Criando estrutura completa para workflow..."
for dir in hooks services store types utils; do
    if [ ! -d "workflow/$dir" ]; then
        mkdir -p workflow/$dir
    fi
done

# 3. Criar estruturas para features vazias

# Dashboard - estrutura completa
echo "📁 Criando estrutura completa para dashboard..."
for dir in hooks services store types utils; do
    if [ ! -d "dashboard/$dir" ]; then
        mkdir -p dashboard/$dir
    fi
done

# Agents - estrutura completa  
echo "�� Criando estrutura completa para agents..."
for dir in hooks services store types utils; do
    if [ ! -d "agents/$dir" ]; then
        mkdir -p agents/$dir
    fi
done

# Chat - adicionar store, utils
echo "📁 Completando estrutura para chat..."
for dir in store utils; do
    if [ ! -d "chat/$dir" ]; then
        mkdir -p chat/$dir
    fi
done

# 4. Adicionar index.ts faltantes
echo "📁 Criando index.ts files onde necessário..."

# Agents
if [ ! -f "agents/index.ts" ]; then
    cat > agents/index.ts << 'AGENTS_INDEX'
/**
 * Agents feature exports
 */

export * from './components';
export * from './hooks';
export * from './services';
export * from './store';
export * from './types';
AGENTS_INDEX
fi

# Dashboard  
if [ ! -f "dashboard/index.ts" ]; then
    cat > dashboard/index.ts << 'DASHBOARD_INDEX'
/**
 * Dashboard feature exports
 */

export * from './components';
export * from './hooks';
export * from './services';
export * from './store';
export * from './types';
DASHBOARD_INDEX
fi

# Chat
if [ ! -f "chat/index.ts" ]; then
    cat > chat/index.ts << 'CHAT_INDEX'
/**
 * Chat feature exports
 */

export * from './components';
export * from './hooks';
export * from './services';
export * from './store';
export * from './types';
CHAT_INDEX
fi

# Tasks
if [ ! -f "tasks/index.ts" ]; then
    cat > tasks/index.ts << 'TASKS_INDEX'
/**
 * Tasks feature exports
 */

export * from './components';
export * from './hooks';
export * from './services';
export * from './store';
export * from './types';
TASKS_INDEX
fi

# Workflow
if [ ! -f "workflow/index.ts" ]; then
    cat > workflow/index.ts << 'WORKFLOW_INDEX'
/**
 * Workflow feature exports
 */

export * from './components';
export * from './hooks';
export * from './services';
export * from './store';
export * from './types';
WORKFLOW_INDEX
fi

echo "✅ Reorganização da estrutura de features concluída!"
echo ""
echo "📊 Estrutura final das features:"
tree . -I node_modules
