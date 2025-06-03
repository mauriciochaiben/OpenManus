#!/bin/bash

echo "🔍 Validando estrutura de features do OpenManus..."
echo "================================================"

# Contadores
total_features=0
complete_features=0

echo ""
echo "🏗️  Verificando estrutura das features..."
echo ""

# Iterar sobre todas as features
for feature in */; do
    feature=${feature%/}  # Remove trailing slash

    # Pular arquivos que não são diretórios de features
    if [[ "$feature" == *.sh ]] || [[ "$feature" == *.md ]]; then
        continue
    fi

    total_features=$((total_features + 1))

    echo "📁 Feature: $feature"

    # Verificar index.ts principal
    if [ -f "$feature/index.ts" ]; then
        echo "  ✅ index.ts (ponto de entrada)"
    else
        echo "  ❌ index.ts (faltando)"
    fi

    # Verificar diretórios
    required_dirs=("components" "hooks" "services" "store" "types" "utils")
    missing_dirs=0

    for dir in "${required_dirs[@]}"; do
        if [ -d "$feature/$dir" ]; then
            if [ -f "$feature/$dir/index.ts" ]; then
                echo "  ✅ $dir/ (com index.ts)"
            else
                echo "  ⚠️  $dir/ (sem index.ts)"
            fi

            # Contar arquivos implementados
            count=$(find "$feature/$dir" -name "*.ts" -o -name "*.tsx" | wc -l | tr -d ' ')
            if [ "$count" -gt 1 ]; then
                echo "    📝 $count arquivos implementados"
            elif [ "$count" -eq 1 ]; then
                echo "    📋 Apenas estrutura (TODO)"
            else
                echo "    📂 Vazio"
            fi
        else
            echo "  ❌ $dir/ (faltando)"
            missing_dirs=$((missing_dirs + 1))
        fi
    done

    if [ $missing_dirs -eq 0 ]; then
        echo "  📊 ✅ Estrutura completa"
        complete_features=$((complete_features + 1))
    else
        echo "  📊 ⚠️  $missing_dirs diretórios faltando"
    fi

    echo ""
done

# Resumo final
echo "================================================"
echo "📊 RESUMO FINAL"
echo "================================================"
echo "Total de features: $total_features"
echo "Features completas: $complete_features"

if [ $total_features -gt 0 ]; then
    percentage=$((complete_features * 100 / total_features))
    echo "Completude: $percentage%"
fi

echo ""
echo "🛠️  SCRIPTS DISPONÍVEIS:"
echo "• ./reorganize_feature.sh [nome] - Reorganizar feature específica"
echo "• ./reorganize_knowledge.sh - Completar feature knowledge"
echo "• ./create_missing_index_files.sh - Criar index.ts faltantes"
echo ""
echo "✅ Validação concluída!"
