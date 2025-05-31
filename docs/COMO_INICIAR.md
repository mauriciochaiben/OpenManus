# 🚀 Como Iniciar o OpenManus

## ✅ Sistema Funcionando

Após a limpeza arquitetural completa, o OpenManus está agora rodando corretamente!

### 🌐 URLs do Sistema

- **Frontend**: http://localhost:3003
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v2/system/health

### 🎯 Métodos de Inicialização

#### Método 1: Script Principal (Recomendado)
```bash
./start_dev.sh
```

#### Método 2: NPM Script
```bash
npm run dev
```

#### Método 3: VS Code Task
- Pressione `Cmd+Shift+P`
- Digite "Tasks: Run Task"
- Selecione "start-openmanus-dev"

### 🔧 Verificações de Sistema

1. **Backend Health Check**:
   ```bash
   curl http://localhost:8000/api/v2/system/health
   ```

2. **Frontend Proxy Test**:
   ```bash
   curl http://localhost:3003/api/v2/system/health
   ```

### 📁 Estrutura Limpa Após Cleanup

```
OpenManus/
├── app/               # Backend principal
├── frontend/          # Frontend React + Vite
├── tests/            # Testes organizados
├── docs/             # Documentação consolidada
├── scripts/          # Utilitários de sistema
├── start_dev.sh      # Script único de entrada
├── main.py           # Entry point principal
└── README.md         # Documentação
```

### 🐛 Resolução de Problemas

**Frontend não conecta?**
- Verifique se o backend está rodando na porta 8000
- Confirme se o frontend está acessível na porta mostrada no terminal
- Verifique se as variáveis de ambiente estão corretas em `frontend/.env`

**Backend não inicia?**
- Ative o ambiente virtual: `source .venv/bin/activate`
- Instale dependências: `pip install -r requirements.txt`
- Verifique se a porta 8000 não está ocupada

### 🎉 Sistema Pronto!

O OpenManus está agora com uma arquitetura limpa e funcionando corretamente. Todas as duplicações foram removidas e a comunicação frontend-backend está estabelecida.
