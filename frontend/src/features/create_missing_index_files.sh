#!/bin/bash

echo "🔨 Criando arquivos index.ts faltantes..."

# Knowledge feature
echo "📁 Processando knowledge..."

# Tasks feature
echo "📁 Processando tasks..."
if [ ! -f "tasks/components/index.ts" ]; then
    cat > tasks/components/index.ts << 'TASKS_COMP'
// Tasks components exports
// TODO: Add task components when implemented
TASKS_COMP
fi

if [ ! -f "tasks/types/index.ts" ]; then
    cat > tasks/types/index.ts << 'TASKS_TYPES'
// Tasks types exports
// TODO: Add task types when implemented
TASKS_TYPES
fi

# Workflow feature
echo "📁 Processando workflow..."
for dir in hooks services store types utils; do
    if [ ! -f "workflow/$dir/index.ts" ]; then
        cat > workflow/$dir/index.ts << EOF_INNER
// Workflow $dir exports
// TODO: Add workflow $dir when implemented
EOF_INNER
    fi
done

# Dashboard feature (todas vazias)
echo "📁 Processando dashboard..."
for dir in components hooks services store types utils; do
    if [ ! -f "dashboard/$dir/index.ts" ]; then
        cat > dashboard/$dir/index.ts << EOF_INNER
// Dashboard $dir exports
// TODO: Add dashboard $dir when implemented
EOF_INNER
    fi
done

# Agents feature (todas vazias)
echo "📁 Processando agents..."
for dir in components hooks services store types utils; do
    if [ ! -f "agents/$dir/index.ts" ]; then
        cat > agents/$dir/index.ts << EOF_INNER
// Agents $dir exports
// TODO: Add agents $dir when implemented
EOF_INNER
    fi
done

# Chat feature
echo "📁 Processando chat..."
for dir in components hooks services store types utils; do
    if [ ! -f "chat/$dir/index.ts" ]; then
        cat > chat/$dir/index.ts << EOF_INNER
// Chat $dir exports
// TODO: Add chat $dir when implemented
EOF_INNER
    fi
done

echo "✅ Arquivos index.ts criados!"
