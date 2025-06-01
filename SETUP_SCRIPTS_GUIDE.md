# OpenManus - Scripts de Inicialização

Este documento descreve os scripts disponíveis para configurar e executar o sistema OpenManus.

## Scripts Disponíveis

### 1. `setup_and_run.py` - Script Principal de Setup e Inicialização

Script completo que verifica todos os requisitos, configura o ambiente e inicia o sistema.

#### Funcionalidades:
- ✅ Verificação de requisitos do sistema (Python, pip, git, Docker)
- ✅ Criação/configuração de ambiente virtual
- ✅ Instalação automática de dependências Python
- ✅ Verificação da estrutura do projeto
- ✅ Configuração do frontend (Node.js/npm)
- ✅ Verificação de serviços externos
- ✅ Testes básicos de funcionalidade
- ✅ Inicialização automática do backend e frontend
- ✅ Monitoramento de saúde dos serviços

#### Uso:
```bash
# Setup completo e inicialização
python3 setup_and_run.py

# Apenas backend
python3 setup_and_run.py --backend-only

# Pular testes de verificação
python3 setup_and_run.py --skip-tests

# Forçar reinstalação de dependências
python3 setup_and_run.py --force-reinstall

# Combinação de opções
python3 setup_and_run.py --backend-only --skip-tests
```

#### Opções de linha de comando:
- `--backend-only`: Executa apenas o backend (sem frontend)
- `--skip-tests`: Pula os testes de verificação
- `--force-reinstall`: Força reinstalação das dependências
- `--help`: Mostra ajuda e exemplos de uso

### 2. `start.sh` - Launcher Simples

Script bash simples que chama o `setup_and_run.py`.

#### Uso:
```bash
# Setup completo
./start.sh

# Com argumentos
./start.sh --backend-only
./start.sh --skip-tests
```

### 3. `quick_test.py` - Teste Rápido do Sistema

Script leve para testar rapidamente se o sistema está funcionando.

#### Funcionalidades:
- ✅ Teste básico do ambiente Python
- ✅ Verificação de imports essenciais
- ✅ Inicialização rápida do backend
- ✅ Teste de conectividade

#### Uso:
```bash
python3 quick_test.py
```

### 4. `start_dev.sh` - Script Original de Desenvolvimento

Script original do projeto para desenvolvimento.

#### Uso:
```bash
./start_dev.sh
```

## Fluxo Recomendado

### Primeira Execução:
```bash
# 1. Clone o repositório
git clone <repo-url>
cd OpenManus

# 2. Execute o setup completo
python3 setup_and_run.py
```

### Execuções Subsequentes:
```bash
# Para desenvolvimento (com reload automático)
python3 setup_and_run.py --skip-tests

# Apenas para testar se está funcionando
python3 quick_test.py

# Script original
./start_dev.sh
```

### Apenas Backend:
```bash
python3 setup_and_run.py --backend-only
```

## Verificação do Sistema

### URLs de Teste:
- **Backend Health**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000 (se disponível)

### Comandos de Verificação:
```bash
# Testar backend
curl http://localhost:8000/health

# Ver logs
tail -f logs/app.log

# Verificar processos
ps aux | grep uvicorn
```

## Resolução de Problemas

### Problemas Comuns:

1. **Erro de importação**:
   ```bash
   python3 setup_and_run.py --force-reinstall
   ```

2. **Porta ocupada**:
   ```bash
   pkill -f uvicorn
   python3 setup_and_run.py
   ```

3. **Problemas de permissão**:
   ```bash
   chmod +x start.sh setup_and_run.py quick_test.py
   ```

4. **Ambiente virtual corrompido**:
   ```bash
   rm -rf .venv
   python3 setup_and_run.py
   ```

### Logs e Debug:

- Logs do sistema: `logs/app.log`
- Saída do script: Terminal onde foi executado
- Verificação de dependências: O script mostra quais pacotes estão instalados

## Arquivos de Configuração

- `requirements.txt`: Dependências Python
- `package.json`: Dependências do frontend
- `config/config.toml`: Configurações do sistema
- `docker-compose.yml`: Configuração Docker

## Status dos Scripts

✅ **setup_and_run.py**: Totalmente funcional, com verificações completas
✅ **start.sh**: Funcional, wrapper simples
✅ **quick_test.py**: Funcional, teste rápido
✅ **start_dev.sh**: Script original preservado

Todos os scripts são executáveis e foram testados no ambiente atual.
