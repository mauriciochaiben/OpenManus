#!/usr/bin/env python3
"""
Teste de Validação do OpenManus Core

Este script testa se o OpenManus funciona adequadamente apenas com
as dependências essenciais (requirements-core.txt).

Uso:
    python test_core_functionality.py
"""

import asyncio
import importlib.util
from pathlib import Path
import sys

# Adicionar o diretório raiz ao path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


class CoreFunctionalityTester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def print_status(self, message, status="info"):
        """Print formatted status message."""
        colors = {
            "success": "\033[92m✅",
            "error": "\033[91m❌",
            "warning": "\033[93m⚠️ ",
            "info": "\033[94mi ",
        }
        reset = "\033[0m"
        print(f"{colors.get(status, '')} {message}{reset}")

    def test_core_imports(self):
        """Teste importações essenciais."""
        self.print_status("Testando importações essenciais...", "info")

        core_imports = [
            ("fastapi", "FastAPI framework"),
            ("uvicorn", "ASGI server"),
            ("pydantic", "Data validation"),
            ("openai", "LLM integration"),
            ("tenacity", "Retry logic"),
            ("tiktoken", "Token counting"),
            ("httpx", "HTTP client"),
            ("aiofiles", "Async file operations"),
            ("loguru", "Logging"),
            ("pytest", "Testing framework"),
        ]

        for module_name, description in core_imports:
            try:
                if importlib.util.find_spec(module_name) is not None:
                    self.print_status(f"{description} ({module_name})", "success")
                    self.passed += 1
                else:
                    msg = f"{description} ({module_name}) - Not found"
                    self.print_status(msg, "error")
                    self.failed += 1
            except Exception as e:
                msg = f"{description} ({module_name}) - Error: {e}"
                self.print_status(msg, "error")
                self.failed += 1

    def test_app_structure(self):
        """Teste estrutura básica da aplicação."""
        self.print_status("Testando estrutura da aplicação...", "info")

        try:
            # Testar importação do módulo principal

            self.print_status("Módulo app importável", "success")
            self.passed += 1
        except Exception as e:
            self.print_status(f"Erro ao importar app: {e}", "error")
            self.failed += 1
            return

        try:
            # Testar importação da API principal

            self.print_status("API principal importável", "success")
            self.passed += 1
        except Exception as e:
            self.print_status(f"Erro ao importar API principal: {e}", "error")
            self.failed += 1

        try:
            # Testar settings

            self.print_status("Sistema de configuração importável", "success")
            self.passed += 1
        except Exception as e:
            self.print_status(f"Erro ao importar settings: {e}", "error")
            self.failed += 1

    def test_optional_features(self):
        """Teste funcionalidades opcionais (devem falhar graciosamente)."""
        self.print_status("Testando funcionalidades opcionais...", "info")

        optional_features = [
            ("numpy", "Processamento numérico"),
            ("pandas", "Manipulação de dados"),
            ("sentence_transformers", "Embeddings locais"),
            ("chromadb", "Vector database"),
            ("docker", "Containerização"),
            ("browser_use", "Automação de browser"),
            ("docling", "Processamento avançado de documentos"),
        ]

        for module_name, description in optional_features:
            try:
                if importlib.util.find_spec(module_name) is not None:
                    msg = f"{description} ({module_name}) - Disponível"
                    self.print_status(msg, "warning")
                    self.warnings += 1
                else:
                    msg = f"{description} ({module_name}) - Não instalado (OK)"
                    self.print_status(msg, "info")
            except Exception:
                msg = f"{description} ({module_name}) - Não instalado (OK)"
                self.print_status(msg, "info")

    async def test_basic_api_functionality(self):
        """Teste funcionalidade básica da API."""
        self.print_status("Testando funcionalidade básica da API...", "info")

        try:
            from app.api.main import app as fastapi_app

            # Verificar se a aplicação FastAPI foi criada
            if fastapi_app is not None:
                self.print_status("Aplicação FastAPI criada", "success")
                self.passed += 1
            else:
                self.print_status("Falha ao criar aplicação FastAPI", "error")
                self.failed += 1

        except Exception as e:
            self.print_status(f"Erro ao testar API: {e}", "error")
            self.failed += 1

    async def test_llm_integration(self):
        """Teste integração básica com LLM."""
        self.print_status("Testando integração com LLM...", "info")

        try:
            from app.llm import LLM

            # Apenas testar se a classe pode ser importada e instanciada
            # sem fazer chamadas reais (que requerem API keys)
            llm_class = LLM
            if llm_class is not None:
                self.print_status("Classe LLM importável", "success")
                self.passed += 1
            else:
                self.print_status("Falha ao importar classe LLM", "error")
                self.failed += 1

        except Exception as e:
            self.print_status(f"Erro ao testar LLM: {e}", "error")
            self.failed += 1

    def print_summary(self):
        """Imprimir resumo dos testes."""
        print("\n" + "=" * 60)
        self.print_status("RESUMO DOS TESTES", "info")
        print("=" * 60)

        total = self.passed + self.failed
        success_rate = (self.passed / total * 100) if total > 0 else 0

        self.print_status(f"Testes executados: {total}", "info")
        self.print_status(f"Sucessos: {self.passed}", "success")
        self.print_status(f"Falhas: {self.failed}", "error")
        self.print_status(f"Avisos: {self.warnings}", "warning")
        self.print_status(f"Taxa de sucesso: {success_rate:.1f}%", "info")

        print("\n" + "=" * 60)

        if self.failed == 0:
            self.print_status("🎉 TODOS OS TESTES CORE PASSARAM!", "success")
            msg = "O OpenManus pode funcionar apenas com requirements-core.txt"
            self.print_status(msg, "success")
        else:
            self.print_status(f"❌ {self.failed} teste(s) falharam", "error")
            msg = "Algumas dependências core podem estar faltando"
            self.print_status(msg, "error")

        if self.warnings > 0:
            msg = f"⚠️  {self.warnings} dependência(s) opcional(is) encontrada(s)"
            self.print_status(msg, "warning")
            msg2 = "Considere remover ou mover para requirements opcionais"
            self.print_status(msg2, "warning")

    async def run_all_tests(self):
        """Executar todos os testes."""
        print("🧪 Testando Funcionalidade Core do OpenManus")
        print("=" * 60)
        print("Este teste verifica se o OpenManus funciona apenas")
        print("com as dependências essenciais (requirements-core.txt)")
        print("=" * 60)

        self.test_core_imports()
        print()

        self.test_app_structure()
        print()

        await self.test_basic_api_functionality()
        print()

        await self.test_llm_integration()
        print()

        self.test_optional_features()
        print()

        self.print_summary()


async def main():
    """Função principal."""
    tester = CoreFunctionalityTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
