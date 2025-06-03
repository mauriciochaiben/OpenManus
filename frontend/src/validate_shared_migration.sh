#!/bin/bash

echo "🔍 Validando estrutura de componentes compartilhados..."
echo "=================================================="

# Verificar estrutura de diretórios compartilhados
echo ""
echo "📁 Estrutura de diretórios compartilhados:"
echo "--------------------------------------------"

BASE_DIR="frontend/src/shared"

for dir in "components" "hooks" "utils" "types"; do
    if [ -d "$BASE_DIR/$dir" ]; then
        echo "✅ $BASE_DIR/$dir/ - existe"

        # Listar arquivos em cada diretório
        files=$(find "$BASE_DIR/$dir" -name "*.ts" -o -name "*.tsx" | wc -l)
        echo "   📄 $files arquivo(s) encontrado(s)"

        if [ "$dir" = "utils" ]; then
            echo "   🔧 Utils disponíveis:"
            for file in "$BASE_DIR/$dir"/*.ts; do
                if [ -f "$file" ]; then
                    basename "$file" .ts | sed 's/^/      - /'
                fi
            done
        fi

        if [ "$dir" = "components" ]; then
            echo "   🧩 Componentes disponíveis:"
            for file in "$BASE_DIR/$dir"/*.tsx; do
                if [ -f "$file" ]; then
                    basename "$file" .tsx | sed 's/^/      - /'
                fi
            done
        fi
    else
        echo "❌ $BASE_DIR/$dir/ - não existe"
    fi
done

echo ""
echo "🔗 Verificação de imports e exports:"
echo "-------------------------------------"

# Verificar se os arquivos index existem
for index_file in "$BASE_DIR/index.ts" "$BASE_DIR/utils/index.ts" "$BASE_DIR/components/index.ts"; do
    if [ -f "$index_file" ]; then
        echo "✅ $(basename $index_file) - existe"
    else
        echo "❌ $(basename $index_file) - não existe"
    fi
done

echo ""
echo "🎯 Verificação de migração de componentes:"
echo "------------------------------------------"

# Verificar SourceSelector
echo "📋 SourceSelector:"
if [ -f "$BASE_DIR/components/SourceSelector.tsx" ]; then
    echo "   ✅ Movido para shared/components/"

    # Verificar se ainda existe na localização original
    if [ -f "frontend/src/features/knowledge/components/SourceSelector.tsx" ]; then
        echo "   ⚠️  Ainda existe na localização original (deveria ser removido)"
    else
        echo "   ✅ Removido da localização original"
    fi
else
    echo "   ❌ Não encontrado em shared/components/"
fi

echo ""
echo "🧪 Verificação de utils migrados:"
echo "-----------------------------------"

# Verificar utils criados
utils=("clipboard" "formatters" "validation")
for util in "${utils[@]}"; do
    if [ -f "$BASE_DIR/utils/$util.ts" ]; then
        echo "✅ $util.ts - criado"

        # Contar funções exportadas
        exports=$(grep -c "^export " "$BASE_DIR/utils/$util.ts" 2>/dev/null || echo "0")
        echo "   📤 $exports função(ões) exportada(s)"
    else
        echo "❌ $util.ts - não encontrado"
    fi
done

echo ""
echo "📊 Resumo da migração:"
echo "----------------------"

total_utils=$(find "$BASE_DIR/utils" -name "*.ts" ! -name "index.ts" | wc -l)
total_components=$(find "$BASE_DIR/components" -name "*.tsx" | wc -l)

echo "🔧 Utils compartilhados: $total_utils"
echo "🧩 Componentes compartilhados: $total_components"

if [ $total_utils -ge 3 ] && [ $total_components -ge 1 ]; then
    echo ""
    echo "🎉 Migração concluída com sucesso!"
    echo "   - Utils centralizados e prontos para uso"
    echo "   - Componentes compartilhados organizados"
    echo "   - Estrutura padronizada implementada"
else
    echo ""
    echo "⚠️  Migração incompleta. Verifique os arquivos em falta."
fi

echo ""
echo "✨ Próximos passos recomendados:"
echo "1. Executar testes para validar a migração"
echo "2. Atualizar imports nas features conforme necessário"
echo "3. Adicionar testes unitários para utils compartilhados"
echo "4. Documentar utils compartilhados com exemplos"
