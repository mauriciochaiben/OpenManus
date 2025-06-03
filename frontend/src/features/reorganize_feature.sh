#!/bin/bash

# Script genérico para reorganizar uma feature
# Uso: ./reorganize_feature.sh [nome_da_feature]

FEATURE_NAME=$1

if [ -z "$FEATURE_NAME" ]; then
    echo "❌ Erro: Especifique o nome da feature"
    echo "Uso: ./reorganize_feature.sh [nome_da_feature]"
    echo ""
    echo "Features disponíveis:"
    ls -1 | grep -v "\.sh$" | grep -v "\.md$"
    exit 1
fi

if [ ! -d "$FEATURE_NAME" ]; then
    echo "❌ Erro: Feature '$FEATURE_NAME' não encontrada"
    exit 1
fi

echo "🔧 Reorganizando feature '$FEATURE_NAME' para estrutura padrão..."

cd "$FEATURE_NAME"

# Criar estrutura padrão de diretórios
echo "📁 Criando estrutura de diretórios..."
mkdir -p components hooks services store types utils

# Função para mover arquivos baseado em padrões
move_files() {
    local pattern=$1
    local destination=$2
    local description=$3

    if find . -maxdepth 1 -name "$pattern" -type f | grep -q .; then
        echo "📦 Movendo $description para $destination/..."
        find . -maxdepth 1 -name "$pattern" -type f -exec git mv {} "$destination/" \;
    fi
}

# Mover componentes React
move_files "*.tsx" "components" "componentes React"

# Mover hooks customizados (exceto index.ts)
move_files "use*.ts" "hooks" "hooks customizados"

# Mover serviços/APIs
move_files "*Service.ts" "services" "serviços"
move_files "*Api.ts" "services" "APIs"
move_files "*api.ts" "services" "APIs"

# Mover stores/estado
move_files "*Store.ts" "store" "stores"
move_files "*store.ts" "store" "stores"

# Mover types (exceto index.ts)
move_files "*Types.ts" "types" "tipos"
move_files "*types.ts" "types" "tipos"

# Mover utilitários
move_files "*Utils.ts" "utils" "utilitários"
move_files "*utils.ts" "utils" "utilitários"
move_files "*Helper.ts" "utils" "helpers"
move_files "*helper.ts" "utils" "helpers"

# Criar arquivos index.ts se não existirem
create_index_if_missing() {
    local dir=$1
    local description=$2

    if [ ! -f "$dir/index.ts" ]; then
        echo "📝 Criando $dir/index.ts..."
        cat > "$dir/index.ts" << EOF
// $description exports
// TODO: Add ${description,,} when implemented
export {};
EOF
    fi
}

create_index_if_missing "components" "Components"
create_index_if_missing "hooks" "Hooks"
create_index_if_missing "services" "Services"
create_index_if_missing "store" "Store"
create_index_if_missing "types" "Types"
create_index_if_missing "utils" "Utils"

echo "✅ Feature '$FEATURE_NAME' reorganizada com sucesso!"
echo ""
echo "📋 Estrutura resultante:"
find . -type f -name "*.ts" -o -name "*.tsx" | sort

echo ""
echo "🚀 Próximos passos:"
echo "1. Verificar se todos os imports estão corretos"
echo "2. Atualizar o arquivo index.ts principal da feature"
echo "3. Executar testes para garantir que nada quebrou"
