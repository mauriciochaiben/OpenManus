# OpenManus - Checklist de Instalação

Use este checklist para verificar se sua instalação do OpenManus está funcionando corretamente.

## ✅ Pré-requisitos do Sistema

- [ ] **Python 3.8+** instalado (`python3 --version`)
- [ ] **Node.js 16+** instalado (`node --version`)
- [ ] **npm** instalado (`npm --version`)
- [ ] **Git** instalado (`git --version`)
- [ ] **Docker** instalado e rodando (opcional, para sandbox features)

## ✅ Configuração do Ambiente

- [ ] Repositório clonado (`git clone https://github.com/mannaandpoem/OpenManus.git`)
- [ ] Ambiente virtual Python criado (`.venv/` existe)
- [ ] Ambiente virtual ativado (`which python` aponta para `.venv/bin/python`)
- [ ] Dependências Python instaladas (`pip list | grep fastapi`)
- [ ] Dependências frontend instaladas (`frontend/node_modules/` existe)

## ✅ Arquivos de Configuração

- [ ] Arquivo `config/config.toml` existe
- [ ] Chaves de API configuradas no `config.toml`
- [ ] Diretórios criados: `logs/`, `uploads/`, `workspace/`

## ✅ Testes de Funcionalidade

### Backend (Python)
- [ ] Importações funcionam: `python -c "from app.config import Config; print('OK')"`
- [ ] API FastAPI inicia: `python frontend_api.py` (deve rodar sem erros)
- [ ] CLI funciona: `python main.py --help` (deve mostrar ajuda)

### Frontend (React)
- [ ] Build funciona: `cd frontend && npm run build`
- [ ] Dev server inicia: `cd frontend && npm run dev`
- [ ] Aplicação carrega em http://localhost:3000

### Integração Completa
- [ ] Script de desenvolvimento funciona: `./dev.sh`
- [ ] Frontend acessa backend: Verificar network tab no browser
- [ ] API docs acessíveis em http://localhost:8000/docs

## ✅ Funcionalidades Opcionais

- [ ] **Playwright**: `playwright --version` (para automação de browser)
- [ ] **Docker**: `docker info` (para sandbox de código)
- [ ] **MCP Tools**: `python run_mcp.py` (deve funcionar sem erro)

## 🔧 Comandos de Teste Rápido

Execute estes comandos para testar rapidamente:

```bash
# Testar backend
source .venv/bin/activate
python -c "from app.agent.manus import Manus; print('✅ Backend OK')"

# Testar frontend
cd frontend
npm run build > /dev/null 2>&1 && echo "✅ Frontend OK" || echo "❌ Frontend Error"
cd ..

# Testar configuração
python -c "from app.config import Config; c=Config(); print('✅ Config OK')" 2>/dev/null || echo "❌ Config Error"
```

## 🚨 Solução de Problemas Comuns

### Erro de Importação Python
```bash
# Verificar se está no ambiente virtual
which python
# Deve apontar para .venv/bin/python

# Reinstalar dependências se necessário
pip install -r requirements.txt
```

### Erro no Frontend
```bash
# Limpar cache e reinstalar
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Erro de Configuração
```bash
# Verificar se o arquivo existe e tem o formato correto
cat config/config.toml
# Deve ter seções [llm] com api_key definida
```

### Erro de Porta em Uso
```bash
# Verificar processos rodando nas portas
lsof -i :8000  # Backend
lsof -i :3000  # Frontend

# Matar processos se necessário
killall python
killall node
```

## 📞 Suporte

Se encontrar problemas:

1. **Consulte os logs**: Verifique arquivos em `logs/`
2. **Verifique issues**: https://github.com/mannaandpoem/OpenManus/issues
3. **Discord**: Entre no servidor da comunidade
4. **Reexecute setup**: `./setup_openmanus.sh` resolve a maioria dos problemas

## ✅ Instalação Completa

Se todos os itens estão marcados, sua instalação está completa! 🎉

Você pode agora:
- Executar `./dev.sh` para desenvolvimento completo
- Executar `python main.py` para uso via terminal
- Acessar http://localhost:3000 para a interface web
- Explorar http://localhost:8000/docs para a documentação da API
