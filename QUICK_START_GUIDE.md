# OpenManus - Guia de Uso Rápido

## Script Único de Inicialização

O OpenManus agora possui um script único que configura e inicializa toda a solução:

```bash
./init_openmanus.sh
```

## Opções Disponíveis

### 🚀 **Modo Desenvolvimento (Recomendado)**
```bash
./init_openmanus.sh --dev
```
- Configura todo o ambiente
- Inicia frontend (React) em http://localhost:3000
- Inicia backend (FastAPI) em http://localhost:8000
- Ideal para desenvolvimento e testes

### 🏭 **Modo Produção**
```bash
./init_openmanus.sh --prod
```
- Configura ambiente
- Executa build otimizado
- Inicia servidor de produção

### 🧪 **Com Testes**
```bash
./init_openmanus.sh --test
```
- Configura ambiente
- Executa todos os testes
- Valida instalação

### 🧹 **Limpeza + Setup**
```bash
./init_openmanus.sh --clean --dev
```
- Remove instalação anterior
- Reconfigura do zero
- Inicia em modo desenvolvimento

### ⚙️ **Apenas Configuração**
```bash
./init_openmanus.sh --setup-only
```
- Apenas instala e configura
- Não inicia serviços

## Primeiro Uso

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/mannaandpoem/OpenManus.git
   cd OpenManus
   ```

2. **Execute o setup inicial:**
   ```bash
   ./init_openmanus.sh --dev
   ```

3. **Configure API keys** (necessário):
   ```bash
   # Edite o arquivo de configuração
   nano config/config.toml

   # Adicione suas chaves de API:
   [llm]
   api_key = "sua-chave-aqui"
   ```

4. **Acesse a aplicação:**
   - **Interface Web:** http://localhost:3000
   - **API Docs:** http://localhost:8000/docs
   - **Backend:** http://localhost:8000

## Verificação de Status

O script cria logs em `logs/init_YYYYMMDD_HHMMSS.log` para debugging.

### Verificar se tudo está funcionando:
```bash
# Verificar processos
ps aux | grep -E "(python|node)"

# Verificar portas
lsof -i :3000  # Frontend
lsof -i :8000  # Backend

# Teste rápido da API
curl http://localhost:8000/health
```

## Solução de Problemas

### Erro de Porta em Uso
```bash
# Parar todos os processos
./init_openmanus.sh --clean

# Matar processos manualmente se necessário
killall python node
```

### Erro de Dependências
```bash
# Reconfigurar do zero
./init_openmanus.sh --clean --dev
```

### Erro de Configuração
```bash
# Verificar arquivo de config
cat config/config.toml

# Usar exemplo se necessário
cp config/examples/config.example.toml config/config.toml
```

## Comandos Úteis

```bash
# Ver ajuda completa
./init_openmanus.sh --help

# Monitorar logs em tempo real
tail -f logs/init_*.log

# Executar apenas testes
python -m pytest tests/ -v

# Usar CLI diretamente
python main.py --help
```

## Desenvolvimento

Para desenvolvimento contínuo, use:

```bash
# Inicia tudo em modo watch
./init_openmanus.sh --dev

# Em outro terminal, execute comandos individuais
python main.py "sua pergunta aqui"
```

O frontend recarrega automaticamente quando você edita arquivos React, e o backend FastAPI também recarrega com mudanças nos arquivos Python.

## Próximos Passos

Após o setup:

1. ✅ Configure suas chaves de API em `config/config.toml`
2. ✅ Teste a interface web em http://localhost:3000
3. ✅ Explore a documentação da API em http://localhost:8000/docs
4. ✅ Execute `python main.py --help` para usar via CLI
5. ✅ Veja exemplos em `examples/`

**Pronto! Seu OpenManus está configurado e rodando! 🎉**
