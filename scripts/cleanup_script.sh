#!/bin/bash
# OpenManus Cleanup Script
# Execute este script para higienizar o projeto

echo "🧹 Iniciando higienização do OpenManus..."

# Criar backup antes da limpeza
echo "📦 Criando backup..."
cp -r . ../OpenManus_backup_$(date +%Y%m%d_%H%M%S)

# Remover arquivos de teste duplicados
echo "🗑️  Removendo testes duplicados na raiz..."
rm -f advanced_test.py
rm -f simple_test.py
rm -f test_multi_agent.py
rm -f test_docling_integration.py
rm -f test_document_reader.py

# Remover arquivos JavaScript experimentais
echo "🗑️  Removendo arquivos JavaScript experimentais..."
rm -f example.spec.js
rm -f test.js
rm -f playwright.config.js

# Remover document readers duplicados
echo "🗑️  Removendo document readers duplicados..."
rm -f app/tool/document_reader_old.py
rm -f app/tool/document_reader_docling.py

# Remover documentação duplicada (manter apenas EN e ZH)
echo "🗑️  Removendo documentação duplicada..."
rm -f README_ja.md
rm -f README_ko.md

# Remover caches
echo "🗑️  Removendo caches..."
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null
find . -name ".DS_Store" -delete 2>/dev/null

# Consolidar documentação multi-agent
echo "📝 Consolidando documentação multi-agent..."
if [ -f "MULTI_AGENT_COMPLETE.md" ]; then
    echo "# Multi-Agent Architecture Summary" > MULTI_AGENT.md
    echo "" >> MULTI_AGENT.md
    cat MULTI_AGENT_IMPLEMENTATION_SUMMARY.md >> MULTI_AGENT.md
    echo "" >> MULTI_AGENT.md
    echo "## Complete Implementation Details" >> MULTI_AGENT.md
    cat MULTI_AGENT_COMPLETE.md >> MULTI_AGENT.md

    rm -f MULTI_AGENT_ARCHITECTURE.md
    rm -f MULTI_AGENT_COMPLETE.md
    rm -f MULTI_AGENT_IMPLEMENTATION_SUMMARY.md
fi

# Criar diretório tests se não existir e mover testes relevantes
echo "📁 Organizando testes..."
mkdir -p tests/integration
if [ -d "tests/sandbox" ]; then
    echo "✅ Testes já organizados em tests/"
fi

echo "✅ Higienização concluída!"
echo "📊 Estatísticas:"
echo "   - Backup criado em: ../OpenManus_backup_$(date +%Y%m%d_%H%M%S)"
echo "   - Arquivos Python restantes: $(find . -name "*.py" -not -path "*/.venv/*" -not -path "*/__pycache__/*" | wc -l)"
echo "   - Espaço liberado: $(du -sh ../OpenManus_backup_* | tail -1 | cut -f1) → $(du -sh . | cut -f1)"
