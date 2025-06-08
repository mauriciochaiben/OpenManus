# Análise de Otimização dos Requirements - OpenManus

## Resumo Executivo

Análise detalhada do uso real das 71 dependências no `requirements.txt` para identificar quais são realmente necessárias e quais podem ser removidas ou tornadas opcionais.

## Categorização das Dependências

### 🔴 CORE - Essenciais (Não podem ser removidas)

| Dependência | Uso Identificado | Justificativa |
|-------------|------------------|---------------|
| `pydantic` | Schema validation, core settings | Framework base para validação |
| `fastapi` | API framework principal | Backend principal |
| `uvicorn` | ASGI server | Servidor para FastAPI |
| `openai` | LLM integration | Integração principal com modelos |
| `tenacity` | Retry logic | Robustez de chamadas API |
| `loguru` | Logging system | Sistema de logs |
| `tiktoken` | Token counting | Contagem de tokens para LLM |
| `aiofiles` | Async file operations | Operações de arquivo assíncronas |
| `httpx` | HTTP client | Cliente HTTP assíncrono |
| `python-multipart` | File uploads | Upload de arquivos via API |
| `websockets` | WebSocket support | Comunicação real-time |
| `python-socketio` | Socket.IO support | Comunicação WebSocket avançada |

### 🟡 FEATURES - Funcionais (Usadas em funcionalidades específicas)

| Dependência | Uso Identificado | Módulos que usam |
|-------------|------------------|------------------|
| `numpy` | Embedding operations | `app/knowledge/services/embedding_service.py` |
| `pandas` | Data processing | `app/tool/document_reader.py`, `app/tool/chart_visualization/` |
| `sentence-transformers` | Local embeddings | `app/knowledge/services/embedding_service.py` |
| `chromadb` | Vector database | `app/knowledge/infrastructure/vector_store_client.py` |
| `langchain` | Text splitting | `app/knowledge/services/source_service.py` |
| `docker` | Code sandboxing | `app/sandbox/`, `app/tool/tool_executor_service.py` |
| `RestrictedPython` | Secure code execution | `app/tool/code_execution.py` |
| `psutil` | Process monitoring | Sistema de sandbox e monitoramento |
| `browser_use` | Browser automation | `app/tool/browser_use_tool.py`, `app/agent/browser.py` |
| `googlesearch-python` | Google search | `app/tool/search/google_search.py` |
| `baidusearch` | Baidu search | `app/tool/search/baidu_search.py` |
| `duckduckgo_search` | DuckDuckGo search | `app/tool/search/duckduckgo_search.py` |
| `requests` | HTTP requests | Várias integrações web |
| `beautifulsoup4` | HTML parsing | Processamento de conteúdo web |
| `boto3` | AWS integration | `app/bedrock.py` (Bedrock LLM) |
| `huggingface-hub` | HuggingFace models | Modelos e embeddings |
| `mcp` | Model Context Protocol | `app/mcp/` (servidores MCP) |

### 🟢 DOCUMENT_PROCESSING - Processamento de Documentos

| Dependência | Uso Identificado | Status |
|-------------|------------------|--------|
| `docling*` | Advanced document processing | **USADO** - `app/tool/document_analyzer.py`, `app/tool/document_reader.py` |
| `python-docx` | DOCX files | **USADO** - `app/knowledge/services/source_service.py` |
| `pillow` | Image processing | **USADO** - Processamento de imagens em documentos |
| `html2text` | HTML to text | **POTENCIAL** - Pode estar sendo usado em conversão |

### 🔵 DEVELOPMENT - Desenvolvimento e Testes

| Dependência | Uso Identificado | Justificativa |
|-------------|------------------|---------------|
| `pytest` | Testing framework | Framework de testes |
| `pytest-asyncio` | Async testing | Testes assíncronos |
| `ruff` | Code linting | Qualidade de código |

### ❌ UNUSED - Não utilizadas (Podem ser removidas)

| Dependência | Status | Observações |
|-------------|--------|-------------|
| `PyPDF2` | **NÃO USADO** | Nenhuma importação encontrada |
| `openpyxl` | **NÃO USADO** | Nenhuma importação encontrada |
| `gymnasium` | **NÃO USADO** | Nenhuma importação encontrada |
| `browsergym` | **NÃO USADO** | Nenhuma importação encontrada |
| `unidiff` | **NÃO USADO** | Nenhuma importação encontrada |
| `playwright` | **NÃO USADO** | Nenhuma importação encontrada no código principal |
| `datasets` | **NÃO USADO** | Apenas no `setup_and_run.py` (desenvolvimento) |
| `colorama` | **NÃO USADO** | Apenas no `setup_and_run.py` (desenvolvimento) |
| `tomli` | **NÃO USADO** | Python 3.11+ tem `tomllib` built-in |
| `setuptools` | **NÃO USADO** | Apenas para packaging |

## Dependências Questionáveis/Opcionais

### 📝 Podem ser tornadas opcionais ou condicionais:

1. **Motores de Busca**
   - `googlesearch-python`, `baidusearch`, `duckduckgo_search`
   - **Sugestão**: Instalar apenas os motores necessários

2. **Processamento de Documentos Avançado**
   - `docling*` (4 pacotes)
   - **Sugestão**: Grupo opcional para análise avançada de documentos

3. **AWS/Cloud**
   - `boto3`
   - **Sugestão**: Opcional, apenas se usar Bedrock

4. **Browser Automation**
   - `browser_use`
   - **Sugestão**: Opcional, para automação web

5. **Embeddings Locais**
   - `sentence-transformers`
   - **Sugestão**: Opcional, usar apenas se não usar OpenAI embeddings

## Recommendations para Requirements Otimizado

### requirements-core.txt (Mínimo funcional)
```txt
# Core framework
pydantic~=2.10.6
fastapi==0.115.9
uvicorn~=0.34.3

# LLM integration
openai~=1.84.0
tenacity~=9.1.2
tiktoken~=0.9.0

# Web and async
httpx>=0.27.0
aiofiles~=24.1.0
python-multipart~=0.0.20

# WebSocket support
python-socketio~=5.13.0
websockets~=15.0.1

# Logging and config
loguru~=0.7.3
pyyaml~=6.0.2

# Basic web
requests~=2.32.3
beautifulsoup4~=4.13.4
```

### requirements-features.txt (Funcionalidades completas)
```txt
# Data processing
numpy
pandas

# Knowledge management
sentence-transformers>=2.2.0
chromadb>=1.0.12
langchain>=0.1.0
langchain-text-splitters>=0.0.1

# Code execution
RestrictedPython>=6.0
psutil>=5.9.0
docker~=7.1.0

# MCP Protocol
mcp~=1.9.2

# Cloud services (optional)
boto3~=1.38.28
huggingface-hub~=0.32.4
```

### requirements-documents.txt (Processamento de documentos)
```txt
# Basic document processing
python-docx~=1.1.2
pillow~=11.2.1
html2text~=2025.4.15

# Advanced document processing with Docling
docling~=2.36.0
docling-core~=2.33.0
docling-ibm-models~=3.4.4
docling-parse~=4.0.1
```

### requirements-search.txt (Motores de busca)
```txt
# Search engines (choose what you need)
googlesearch-python~=1.3.0
baidusearch~=1.0.3
duckduckgo_search~=8.0.2
```

### requirements-browser.txt (Automação web)
```txt
# Browser automation
browser_use~=0.1.40
```

### requirements-dev.txt (Desenvolvimento)
```txt
# Testing
pytest~=8.4.0
pytest-asyncio~=0.26.0

# Code quality
ruff~=0.11.12
```

## Impacto da Otimização

### Redução Estimada:
- **De 71 para ~25 dependências core** (redução de ~65%)
- **Tempo de instalação**: Redução estimada de 60-70%
- **Tamanho do ambiente**: Redução estimada de 50-60%
- **Complexidade**: Muito menor superficie de ataque e debug

### Benefícios:
1. ✅ **Inicialização mais rápida**
2. ✅ **Menos conflitos de dependências**
3. ✅ **Instalação mais confiável**
4. ✅ **Menor superficie de ataque de segurança**
5. ✅ **Debug mais fácil**
6. ✅ **Containers menores**

### Próximos Passos:
1. Validar se funcionalidades funcionam sem as dependências "não usadas"
2. Criar requirements modular
3. Testar sistema com requirements-core apenas
4. Implementar instalação condicional de features
