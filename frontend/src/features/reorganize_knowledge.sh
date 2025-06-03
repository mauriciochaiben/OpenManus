#!/bin/bash

echo "🔧 Reorganizando feature 'knowledge' para estrutura padrão..."

cd /Users/mauriciochaiben/OpenManus/frontend/src/features/knowledge

# Criar diretórios faltantes
echo "📁 Criando diretórios faltantes..."
mkdir -p store
mkdir -p utils

# Criar arquivos index.ts para os novos diretórios
echo "📝 Criando arquivos index.ts..."

# Store index
cat > store/index.ts << 'EOF'
// Knowledge store exports
// TODO: Add knowledge store when implemented
export {};
EOF

# Utils index
cat > utils/index.ts << 'EOF'
// Knowledge utils exports
// TODO: Add knowledge utilities when implemented
export {};
EOF

echo "✅ Feature 'knowledge' reorganizada com sucesso!"
echo "📋 Estrutura atual:"
tree . -I node_modules
