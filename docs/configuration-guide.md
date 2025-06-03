# Guia de Configuração Centralizada - OpenManus

## Visão Geral

O OpenManus agora utiliza um sistema de configuração centralizado baseado em Pydantic BaseSettings, que oferece:

- **Carregamento hierárquico**: Variáveis de ambiente > TOML por ambiente > TOML base > valores padrão
- **Validação automática**: Tipos e valores são validados automaticamente pelo Pydantic
- **Configurações estruturadas**: Organização em grupos lógicos (LLM, Browser, Search, etc.)
- **Suporte a múltiplos ambientes**: development, staging, production, testing
- **Retrocompatibilidade**: Código antigo continua funcionando com warnings de depreciação

## Estrutura de Arquivos

```
config/
├── config.toml              # Configuração base
├── development.toml         # Overrides para desenvolvimento
├── production.toml          # Overrides para produção
├── mcp.specialized.json     # Configurações MCP específicas
└── examples/                # Exemplos de configuração
    ├── config.example.toml
    ├── config.example-model-anthropic.toml
    ├── config.example-model-azure.toml
    ├── config.example-model-google.toml
    ├── config.example-model-ollama.toml
    └── config.example-model-ppio.toml
```

## Como Usar

### Importação Básica

```python
# Nova forma recomendada
from app.core.settings import settings

# Acessar configurações
print(f"Ambiente: {settings.environment}")
print(f"Debug: {settings.debug}")
print(f"LLM Model: {settings.llm_model}")
```

### Configurações Estruturadas

```python
# Configurações de LLM
llm_configs = settings.llm_configs
primary_llm = llm_configs.get("primary", {})
print(f"Model: {primary_llm.model}")
print(f"API Type: {primary_llm.api_type}")

# Configurações de Knowledge Management
knowledge = settings.knowledge_config
vector_db = knowledge.vector_db
print(f"Vector DB: {vector_db.host}:{vector_db.port}")

# Configurações de Browser
browser = settings.browser_config
if browser:
    print(f"Headless: {browser.headless}")
    print(f"Security disabled: {browser.disable_security}")

# Configurações de Search
search = settings.search_config
print(f"Engine: {search.engine}")
print(f"Fallbacks: {search.fallback_engines}")
```

### Configurações por Ambiente

As configurações são carregadas na seguinte ordem de prioridade:

1. **Variáveis de ambiente** (maior prioridade)
2. **Arquivo específico do ambiente** (`development.toml`, `production.toml`, etc.)
3. **Arquivo base** (`config.toml`)
4. **Valores padrão** do código (menor prioridade)

#### Exemplo de Override por Ambiente

**config.toml** (base):
```toml
[llm]
model = "gpt-4o-mini"
max_tokens = 4096
temperature = 0.7

[browser]
headless = true
```

**development.toml** (override):
```toml
[llm]
model = "gpt-4o-mini"  # Modelo menor para desenvolvimento
max_tokens = 2048      # Menos tokens para economia

[browser]
headless = false       # Browser visível para debug
```

#### Variáveis de Ambiente

```bash
# Override via variáveis de ambiente
export ENVIRONMENT=production
export LLM__MODEL=gpt-4  # Usar __ para nested configs
export DEBUG=false
export LOG_LEVEL=ERROR
```

## Configurações Disponíveis

### Core Application
- `environment`: Ambiente atual (development, staging, production, testing)
- `debug`: Modo debug
- `log_level`: Nível de logging

### LLM Configuration
- `llm_model`: Modelo padrão
- `llm_api_key`: Chave da API
- `llm_base_url`: URL base da API
- `llm_max_tokens`: Tokens máximos
- `llm_temperature`: Temperatura do modelo

### Browser Configuration
- `browser_headless`: Modo headless
- `browser_disable_security`: Desabilitar segurança
- `browser_max_content_length`: Tamanho máximo do conteúdo

### Search Configuration
- `search_engine`: Motor de busca principal
- `search_retry_delay`: Delay entre tentativas
- `search_lang`: Idioma das buscas

### Vector Database
- `vector_db_host`: Host do banco vetorial
- `vector_db_port`: Porta do banco vetorial
- `vector_collection_name`: Nome da coleção de documentos

### Document Processing
- `document_storage_path`: Caminho de armazenamento
- `document_max_size_bytes`: Tamanho máximo de arquivo
- `vector_chunk_size`: Tamanho dos chunks

## Configurações MCP Especializadas

O sistema agora suporta configurações específicas para servidores MCP especializados:

```toml
[mcp.specialized.coordination]
capabilities = "task_routing,memory_sharing,inter_agent_communication"
max_agents = 10
memory_limit = "256MB"

[mcp.specialized.research]
tools = "web_search,data_analysis,document_processing"
max_concurrent_searches = 5
cache_results = true

[mcp.specialized.development]
tools = "filesystem,code_execution,git,testing"
sandbox_enabled = true
code_timeout = 60
```

## Migração de Código Antigo

### Código Antigo (depreciado)
```python
from app.config import config
llm_model = config.llm_model
```

### Código Novo (recomendado)
```python
from app.core.settings import settings
llm_model = settings.llm_model
```

### Retrocompatibilidade

O código antigo ainda funciona mas emite warnings de depreciação:

```python
# Ainda funciona, mas com warning
from app.config import config  # DeprecationWarning
llm_configs = config.llm       # DeprecationWarning

# Alias também disponível
from app.core.settings import config  # OK, sem warning
```

## Validação e Debugging

### Script de Validação

Execute o script de validação para verificar se tudo está funcionando:

```bash
python scripts/validate_config_refactoring.py
```

### Debug de Configurações

```python
from app.core.settings import settings

# Ver configuração carregada
print(f"Environment: {settings.environment}")
print(f"Config dir: {settings.config_dir}")

# Ver configuração TOML carregada
toml_config = settings._load_toml_config()
print("TOML config loaded:", toml_config.keys())

# Ver configurações específicas
print("LLM configs:", len(settings.llm_configs))
print("Knowledge config:", settings.knowledge_config.vector_db.host)
```

## Boas Práticas

### 1. Use Configurações Estruturadas
```python
# ✅ Bom - usa configuração estruturada
knowledge_config = settings.knowledge_config
chunk_size = knowledge_config.document_processing.chunk_size

# ❌ Evitar - acesso direto a campos individuais
chunk_size = settings.vector_chunk_size
```

### 2. Valide Configurações no Código
```python
def init_vector_store():
    config = settings.knowledge_config.vector_db
    if not config.url:
        raise ValueError("Vector DB URL não configurada")
    return VectorStore(config.url)
```

### 3. Use Configurações por Ambiente
- Mantenha configurações sensíveis apenas em arquivos de produção
- Use configurações de desenvolvimento para debug/testing
- Documente overrides específicos de ambiente

### 4. Evite Hardcoding
```python
# ✅ Bom - usa configuração
max_tokens = settings.llm_configs["primary"].max_tokens

# ❌ Evitar - hardcoded
max_tokens = 4096
```

## Troubleshooting

### Configuração não carregada
- Verifique se o arquivo TOML existe e está bem formado
- Confirme se a variável `ENVIRONMENT` está definida corretamente
- Use o script de validação para diagnóstico

### Valores não sendo aplicados
- Lembre-se da ordem de prioridade: env vars > env file > base file > defaults
- Verifique nomes de variáveis de ambiente (use `__` para nested configs)
- Confirme se os tipos estão corretos (string, int, bool, etc.)

### Retrocompatibilidade
- Warnings de depreciação são normais durante a transição
- Migre gradualmente usando o novo sistema
- Teste thor
