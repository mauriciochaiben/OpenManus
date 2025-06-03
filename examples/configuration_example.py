"""
Exemplo prático de uso do sistema de configuração centralizado
Demonstra como diferentes partes do sistema podem acessar configurações
de forma consistente e segura.
"""

from app.core.settings import settings
from app.logger import logger


class ExampleLLMService:
    """Exemplo de serviço que usa configurações centralizadas"""

    def __init__(self):
        # Acesso a configurações LLM estruturadas
        self.llm_configs = settings.llm_configs
        self.primary_config = self.llm_configs.get("primary")

        if not self.primary_config:
            raise ValueError("Configuração LLM primária não encontrada")

        logger.info(f"Initialized LLM service with model: {self.primary_config.model}")
        logger.info(f"API Type: {self.primary_config.api_type}")
        logger.info(f"Max tokens: {self.primary_config.max_tokens}")

    def get_fallback_config(self):
        """Exemplo de acesso a configuração de fallback"""
        return {k: v for k, v in self.llm_configs.items() if k != "primary"}

    def validate_config(self):
        """Valida se a configuração está completa"""
        required_fields = ["model", "api_key", "base_url"]
        for field in required_fields:
            if not getattr(self.primary_config, field, None):
                raise ValueError(f"Campo obrigatório '{field}' não configurado")
        return True


class ExampleBrowserService:
    """Exemplo de serviço de browser usando configurações"""

    def __init__(self):
        self.browser_config = settings.browser_config

        if not self.browser_config:
            logger.warning("Browser config não configurado, usando valores padrão")
            return

        logger.info(f"Browser headless: {self.browser_config.headless}")
        logger.info(f"Security disabled: {self.browser_config.disable_security}")

        if self.browser_config.proxy:
            logger.info(f"Proxy configured: {self.browser_config.proxy.server}")

    def get_browser_args(self):
        """Constrói argumentos do browser baseado na configuração"""
        args = []

        if not self.browser_config:
            return args

        if self.browser_config.headless:
            args.append("--headless")

        if self.browser_config.disable_security:
            args.extend(
                ["--disable-web-security", "--disable-features=VizDisplayCompositor"]
            )

        args.extend(self.browser_config.extra_chromium_args)

        return args


class ExampleVectorStoreService:
    """Exemplo de serviço de vector store usando configurações de knowledge"""

    def __init__(self):
        self.knowledge_config = settings.knowledge_config
        self.vector_config = self.knowledge_config.vector_db
        self.embedding_config = self.knowledge_config.embedding

        logger.info(f"Vector DB: {self.vector_config.url}")
        logger.info(f"Documents collection: {self.vector_config.documents_collection}")
        logger.info(f"Embedding model: {self.embedding_config.model_name}")

    def get_connection_params(self):
        """Retorna parâmetros de conexão do vector store"""
        params = {
            "host": self.vector_config.host,
            "port": self.vector_config.port,
            "collection_name": self.vector_config.documents_collection,
        }

        if self.vector_config.auth_token:
            params["auth_token"] = self.vector_config.auth_token
            params["auth_header"] = self.vector_config.auth_header

        return params

    def get_embedding_params(self):
        """Retorna parâmetros de embedding"""
        return {
            "model_name": self.embedding_config.model_name,
            "dimension": self.embedding_config.dimension,
            "normalize": self.embedding_config.normalize,
            "batch_size": self.embedding_config.batch_size,
        }


class ExampleUploadService:
    """Exemplo de serviço de upload usando configurações centralizadas"""

    def __init__(self):
        # Usa a propriedade computed upload_config
        self.upload_config = settings.upload_config
        self.upload_dir = settings.upload_dir

        logger.info(f"Upload directory: {self.upload_dir}")
        logger.info(f"Max file size: {self.upload_config['max_file_size']}")
        logger.info(f"Allowed extensions: {self.upload_config['allowed_extensions']}")

    def validate_upload(self, filename: str, file_size: int):
        """Valida upload baseado nas configurações"""
        # Verifica extensão
        extension = filename.split(".")[-1].lower()
        if extension not in self.upload_config["allowed_extensions"]:
            raise ValueError(f"Extensão '{extension}' não permitida")

        # Verifica tamanho (converte string como "50MB" para bytes)
        max_size_str = self.upload_config["max_file_size"]
        max_size_bytes = self._parse_size(max_size_str)

        if file_size > max_size_bytes:
            raise ValueError(f"Arquivo muito grande: {file_size} > {max_size_bytes}")

        return True

    def _parse_size(self, size_str: str) -> int:
        """Converte string de tamanho para bytes"""
        size_str = size_str.upper()
        if size_str.endswith("MB"):
            return int(size_str[:-2]) * 1024 * 1024
        if size_str.endswith("KB"):
            return int(size_str[:-2]) * 1024
        if size_str.endswith("GB"):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        return int(size_str)


class ExampleEnvironmentAwareService:
    """Exemplo de serviço que se adapta ao ambiente"""

    def __init__(self):
        self.environment = settings.environment
        self.debug = settings.debug
        self.log_level = settings.log_level

        # Configurações específicas por ambiente
        self.timeout = self._get_timeout_for_environment()
        self.retry_count = self._get_retry_count_for_environment()

        logger.info(f"Service initialized for environment: {self.environment}")
        logger.info(f"Timeout: {self.timeout}s, Retries: {self.retry_count}")

    def _get_timeout_for_environment(self) -> int:
        """Retorna timeout apropriado para o ambiente"""
        timeouts = {
            "development": 10,  # Timeout menor para desenvolvimento
            "staging": 30,  # Timeout médio para staging
            "production": 60,  # Timeout maior para produção
            "testing": 5,  # Timeout mínimo para testes
        }
        return timeouts.get(self.environment, 30)

    def _get_retry_count_for_environment(self) -> int:
        """Retorna número de tentativas apropriado para o ambiente"""
        retries = {
            "development": 1,  # Menos tentativas em desenvolvimento
            "staging": 2,  # Tentativas médias em staging
            "production": 3,  # Mais tentativas em produção
            "testing": 0,  # Sem tentativas em testes
        }
        return retries.get(self.environment, 2)


def demonstrate_configuration_usage():
    """Demonstra o uso prático das configurações"""

    print("🚀 Demonstração do Sistema de Configuração Centralizado\n")

    # Informações básicas do ambiente
    print(f"📊 Ambiente atual: {settings.environment}")
    print(f"🐛 Debug mode: {settings.debug}")
    print(f"📝 Log level: {settings.log_level}")
    print(f"📁 Project root: {settings.project_root}")
    print(f"⚙️  Config dir: {settings.config_dir}")
    print()

    # Inicializar serviços de exemplo
    print("🔧 Inicializando serviços com configurações centralizadas...")

    try:
        ExampleLLMService()
        print("✅ LLM Service inicializado")
    except Exception as e:
        print(f"❌ Erro no LLM Service: {e}")

    try:
        browser_service = ExampleBrowserService()
        print("✅ Browser Service inicializado")
        args = browser_service.get_browser_args()
        print(f"   Browser args: {args}")
    except Exception as e:
        print(f"❌ Erro no Browser Service: {e}")

    try:
        vector_service = ExampleVectorStoreService()
        print("✅ Vector Store Service inicializado")
        params = vector_service.get_connection_params()
        print(f"   Connection params: {list(params.keys())}")
    except Exception as e:
        print(f"❌ Erro no Vector Store Service: {e}")

    try:
        upload_service = ExampleUploadService()
        print("✅ Upload Service inicializado")
        # Teste de validação
        upload_service.validate_upload("test.pdf", 1024 * 1024)  # 1MB
        print("   Validação de upload passou")
    except Exception as e:
        print(f"❌ Erro no Upload Service: {e}")

    try:
        ExampleEnvironmentAwareService()
        print("✅ Environment-Aware Service inicializado")
        print("   Configurações por ambiente aplicadas")
    except Exception as e:
        print(f"❌ Erro no Environment-Aware Service: {e}")

    print()
    print("📋 Resumo das Configurações Carregadas:")

    # Mostrar resumo das configurações
    llm_configs = settings.llm_configs
    print(f"   🤖 LLM configs: {len(llm_configs)} configurações")

    browser_config = settings.browser_config
    if browser_config:
        print(f"   🌐 Browser: headless={browser_config.headless}")

    search_config = settings.search_config
    print(f"   🔍 Search: engine={search_config.engine}")

    knowledge_config = settings.knowledge_config
    print(
        f"   🧠 Vector DB: {knowledge_config.vector_db.host}:{knowledge_config.vector_db.port}"
    )

    mcp_config = settings.mcp_config
    print(f"   🤖 MCP servers: {len(mcp_config.servers)} configurados")

    print("\n✅ Demonstração concluída com sucesso!")


if __name__ == "__main__":
    demonstrate_configuration_usage()
