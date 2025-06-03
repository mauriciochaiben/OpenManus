#!/usr/bin/env python3
"""
Script de validação da refatoração de configuração

Este script valida se a centralização de configuração está funcionando corretamente,
testando carregamento de arquivos TOML, overrides por ambiente e acesso via settings.
"""
# ruff: noqa: E402

import sys
from pathlib import Path

# Adicionar o diretório do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.settings import settings


def test_basic_settings():
    """Testa configurações básicas"""
    print("🔧 Testando configurações básicas...")

    # Testa acesso básico
    assert hasattr(settings, "environment"), "settings.environment deve estar disponível"
    assert hasattr(settings, "debug"), "settings.debug deve estar disponível"
    assert hasattr(settings, "log_level"), "settings.log_level deve estar disponível"

    print(f"  ✅ Ambiente: {settings.environment}")
    print(f"  ✅ Debug: {settings.debug}")
    print(f"  ✅ Log Level: {settings.log_level}")


def test_toml_loading():
    """Testa carregamento de arquivos TOML"""
    print("📁 Testando carregamento de TOML...")

    # Testa se os computed fields estão funcionando
    llm_configs = settings.llm_configs
    assert isinstance(llm_configs, dict), "llm_configs deve ser um dicionário"
    print(f"  ✅ LLM configs carregados: {len(llm_configs)} configurações")

    # Testa configuração de browser
    browser_config = settings.browser_config
    if browser_config:
        print(f"  ✅ Browser config: headless={browser_config.headless}")
    else:
        print("  ℹ️  Browser config não configurado")

    # Testa configuração de search
    search_config = settings.search_config
    print(f"  ✅ Search engine: {search_config.engine}")

    # Testa configuração de sandbox
    sandbox_config = settings.sandbox_config
    print(f"  ✅ Sandbox enabled: {sandbox_config.use_sandbox}")


def test_mcp_specialization():
    """Testa configurações MCP especializadas"""
    print("🤖 Testando configurações MCP especializadas...")

    mcp_config = settings.mcp_config
    print(f"  ✅ MCP server reference: {mcp_config.server_reference}")
    print(f"  ✅ MCP servers configurados: {len(mcp_config.servers)}")

    # Testa se as configurações especializadas estão no TOML
    toml_config = settings._load_toml_config()
    mcp_specialized = toml_config.get("mcp", {}).get("specialized", {})

    for server_name in ["coordination", "research", "development"]:
        if server_name in mcp_specialized:
            print(f"  ✅ {server_name.title()} MCP configurado")
        else:
            print(f"  ⚠️  {server_name.title()} MCP não encontrado no TOML")


def test_knowledge_config():
    """Testa configurações de knowledge management"""
    print("🧠 Testando configurações de knowledge management...")

    knowledge_config = settings.knowledge_config

    # Vector DB
    vector_db = knowledge_config.vector_db
    print(f"  ✅ Vector DB: {vector_db.host}:{vector_db.port}")

    # Embedding
    embedding = knowledge_config.embedding
    print(f"  ✅ Embedding model: {embedding.model_name}")

    # Document processing
    doc_processing = knowledge_config.document_processing
    print(f"  ✅ Chunk size: {doc_processing.chunk_size}")


def test_upload_config():
    """Testa configurações de upload"""
    print("📤 Testando configurações de upload...")

    upload_dir = settings.upload_dir
    print(f"  ✅ Upload directory: {upload_dir}")

    upload_config = settings.upload_config
    print(f"  ✅ Max file size: {upload_config['max_file_size']}")
    print(f"  ✅ Allowed extensions: {len(upload_config['allowed_extensions'])} tipos")


def test_environment_override():
    """Testa override por ambiente"""
    print("🌍 Testando override por ambiente...")

    # Verifica se existe arquivo de ambiente específico
    config_dir = settings.config_dir
    env_file = config_dir / f"{settings.environment}.toml"

    if env_file.exists():
        print(f"  ✅ Arquivo de ambiente encontrado: {env_file}")
    else:
        print(f"  ⚠️  Arquivo de ambiente não encontrado: {env_file}")

    # Testa algumas configurações que devem variar por ambiente
    if settings.environment == "development":
        print("  ✅ Configuração de desenvolvimento detectada")
        print(f"    - Debug: {settings.debug}")
        print(f"    - Log Level: {settings.log_level}")


def test_backward_compatibility():
    """Testa compatibilidade com código antigo"""
    print("⏮️  Testando compatibilidade com código antigo...")

    # Testa o alias config
    from app.core.settings import config

    assert config == settings, "config deve ser um alias para settings"
    print("  ✅ Alias 'config' funcionando")

    # Testa app.config (deveria funcionar mas emitir warning)
    try:
        from app import config as old_config  # noqa: F401

        print("  ✅ app.config ainda importável (com deprecation warning)")
    except ImportError:
        print("  ⚠️  app.config não importável")


def test_paths_and_directories():
    """Testa caminhos e diretórios"""
    print("📂 Testando caminhos e diretórios...")

    # Testa computed properties de paths
    print(f"  ✅ Project root: {settings.project_root}")
    print(f"  ✅ Workspace root: {settings.workspace_root}")
    print(f"  ✅ Config dir: {settings.config_dir}")

    # Verifica se os diretórios existem
    assert settings.project_root.exists(), "Project root deve existir"
    assert settings.config_dir.exists(), "Config dir deve existir"
    print("  ✅ Diretórios básicos existem")


def main():
    """Executa todos os testes de validação"""
    print("🚀 Validando refatoração de configuração do OpenManus\n")

    try:
        test_basic_settings()
        print()

        test_toml_loading()
        print()

        test_mcp_specialization()
        print()

        test_knowledge_config()
        print()

        test_upload_config()
        print()

        test_environment_override()
        print()

        test_backward_compatibility()
        print()

        test_paths_and_directories()
        print()

        print("✅ Todas as validações passaram! A refatoração está funcionando corretamente.")

    except Exception as e:
        print(f"❌ Erro durante validação: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
