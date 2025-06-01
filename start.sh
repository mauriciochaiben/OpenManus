#!/bin/bash

# OpenManus - Script de Inicialização Simples
# Uso: ./start.sh [backend-only] [skip-tests] [force-reinstall]

echo "🚀 Iniciando OpenManus..."

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale Python 3.8+ primeiro."
    exit 1
fi

# Executar o script Python principal
python3 setup_and_run.py "$@"
