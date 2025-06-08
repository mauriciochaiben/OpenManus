# 🚀 Guia Rápido: Sistema Modular OpenManus

## Como usar o novo sistema de dependências otimizado

### 📦 Instalação Rápida (Recomendada)

```bash
# Apenas essencial - para desenvolvimento básico
python install_dependencies.py --core

# Core + funcionalidades avançadas - para uso completo
python install_dependencies.py --core --features

# Ver todas as opções disponíveis
python install_dependencies.py --list
```

### 🎯 Cenários de Uso

#### 1. Desenvolvimento API Básico
```bash
# Para desenvolvimento de APIs simples
python install_dependencies.py --core
# ✅ 19 dependências - instalação em ~1-2 minutos
```

#### 2. Processamento de Documentos
```bash
# Para análise de PDFs, Word, etc.
python install_dependencies.py --core --documents
# ✅ 25 dependências - inclui Docling e processadores
```

#### 3. Automação Web
```bash
# Para scraping e automação de browser
python install_dependencies.py --core --browser --search
# ✅ 23 dependências - inclui browser automation e motores de busca
```

#### 4. Sistema Completo
```bash
# Todas as funcionalidades (equivale ao requirements.txt original)
python install_dependencies.py --all
# ✅ 39 dependências - ainda 45% menor que o original
```

### 🔍 Verificação do Sistema

```bash
# Testar se tudo está funcionando
python test_core_functionality.py
```

### 📊 Comparação de Performance

| Configuração | Dependências | Tempo Instalação | Uso Recomendado |
|--------------|--------------|------------------|-----------------|
| Core | 19 | ~1-2 min | APIs básicas, desenvolvimento |
| Core + Features | 29 | ~2-3 min | Uso geral recomendado |
| Core + Documents | 25 | ~2-3 min | Processamento de documentos |
| All | 39 | ~3-4 min | Funcionalidades completas |
| Original | 71 | ~8-10 min | ❌ Não recomendado |

### 🆘 Solução de Problemas

#### Se algo não funcionar após instalação modular:

1. **Verificar dependências:**
   ```bash
   python test_core_functionality.py
   ```

2. **Instalar módulo adicional:**
   ```bash
   # Se precisar de processamento de documentos
   python install_dependencies.py --documents
   ```

3. **Voltar ao sistema completo:**
   ```bash
   python install_dependencies.py --all
   ```

### 💡 Dicas de Otimização

- ✅ **Comece sempre com `--core`**
- ✅ **Adicione módulos conforme necessário**
- ✅ **Use `--dry-run` para ver o que será instalado**
- ✅ **Combine módulos: `--core --features --documents`**

### 🏗️ Para Desenvolvedores

#### Dockerfile otimizado:
```dockerfile
# Instalar apenas core por padrão
COPY requirements-core.txt .
RUN pip install -r requirements-core.txt

# Features opcionais baseadas em build args
ARG FEATURES=false
COPY requirements-features.txt .
RUN if [ "$FEATURES" = "true" ]; then pip install -r requirements-features.txt; fi
```

#### Virtual Environment limpo:
```bash
# Criar ambiente limpo
python -m venv venv-openmanus
source venv-openmanus/bin/activate  # Linux/Mac
# ou
venv-openmanus\Scripts\activate  # Windows

# Instalar apenas o necessário
python install_dependencies.py --core --features
```

---

**⚡ Resultado: Sistema 45% mais rápido e leve!**
