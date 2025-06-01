#!/usr/bin/env python3
"""
OpenManus - Setup and Run Script

Script único que verifica todos os requisitos do ambiente,
configura automaticamente se necessário e inicializa o sistema.

Uso:
    python setup_and_run.py [--backend-only] [--skip-tests] [--force-reinstall]

Opções:
    --backend-only      Executa apenas o backend (sem frontend)
    --skip-tests        Pula os testes de verificação
    --force-reinstall   Força reinstalação das dependências
    --help              Mostra esta mensagem
"""

import argparse
import json
import os
import platform
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import venv
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# Cores para output
class Colors:
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    WHITE = "\033[1;37m"
    NC = "\033[0m"  # No Color


def print_colored(message: str, color: str = Colors.NC):
    """Print colorized message"""
    print(f"{color}{message}{Colors.NC}")


def print_step(step: str):
    """Print step with formatting"""
    print_colored(f"\n🔧 {step}", Colors.BLUE)


def print_success(message: str):
    """Print success message"""
    print_colored(f"✅ {message}", Colors.GREEN)


def print_warning(message: str):
    """Print warning message"""
    print_colored(f"⚠️  {message}", Colors.YELLOW)


def print_error(message: str):
    """Print error message"""
    print_colored(f"❌ {message}", Colors.RED)


def print_info(message: str):
    """Print info message"""
    print_colored(f"ℹ️  {message}", Colors.CYAN)


class OpenManusSetup:
    def __init__(self, args):
        self.args = args
        self.project_root = Path(__file__).parent.absolute()
        self.venv_path = self.project_root / ".venv"
        self.python_executable = None
        self.services_pids = {}

        # Configurações
        self.required_python_version = (3, 8)
        self.required_packages = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "openai",
            "tenacity",
            "loguru",
            "numpy",
            "datasets",
            "tiktoken",
            "html2text",
            "pillow",
            "aiofiles",
            "websockets",
            "pytest",
            "pytest-asyncio",
            "mcp",
            "httpx",
            "docker",
            "RestrictedPython",
            "psutil",
        ]
        self.optional_packages = ["node", "npm", "docker"]

    def run(self):
        """Executa todo o processo de setup e inicialização"""
        try:
            print_colored(
                "🚀 OpenManus - Setup e Inicialização Automática", Colors.WHITE
            )
            print_colored("=" * 60, Colors.WHITE)

            # Verificações de sistema
            self.check_system_requirements()

            # Setup do ambiente Python
            self.setup_python_environment()

            # Instalação de dependências
            self.install_dependencies()

            # Verificação do projeto
            self.verify_project_structure()

            # Setup do frontend (se necessário)
            if not self.args.backend_only:
                self.setup_frontend()

            # Verificação dos serviços externos
            self.check_external_services()

            # Testes de verificação
            if not self.args.skip_tests:
                self.run_verification_tests()

            # Inicialização do sistema
            self.start_system()

        except KeyboardInterrupt:
            print_warning("\nInterrompido pelo usuário")
            self.cleanup()
            sys.exit(1)
        except Exception as e:
            print_error(f"Erro durante setup: {str(e)}")
            self.cleanup()
            sys.exit(1)

    def check_system_requirements(self):
        """Verifica requisitos do sistema"""
        print_step("Verificando requisitos do sistema")

        # Verificar Python
        if sys.version_info < self.required_python_version:
            print_error(
                f"Python {'.'.join(map(str, self.required_python_version))}+ necessário. "
                f"Encontrado: {sys.version}"
            )
            sys.exit(1)

        print_success(f"Python {sys.version.split()[0]} ✓")

        # Verificar pip
        try:
            import pip

            print_success("pip ✓")
        except ImportError:
            print_error("pip não encontrado. Instale pip primeiro.")
            sys.exit(1)

        # Verificar git
        if shutil.which("git"):
            print_success("git ✓")
        else:
            print_warning("git não encontrado (opcional)")

        # Verificar sistema operacional
        system = platform.system()
        print_success(f"Sistema operacional: {system} ✓")

        # Verificar Docker (opcional)
        if shutil.which("docker"):
            try:
                result = subprocess.run(
                    ["docker", "--version"], capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    print_success("Docker ✓")
                else:
                    print_warning("Docker instalado mas não funcional")
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                print_warning("Docker não funcional")
        else:
            print_warning("Docker não encontrado (recomendado para sandbox)")

    def setup_python_environment(self):
        """Configura ambiente virtual Python"""
        print_step("Configurando ambiente Python")

        if self.venv_path.exists() and not self.args.force_reinstall:
            print_info("Ambiente virtual encontrado")
            self.python_executable = self.get_venv_python()
        else:
            if self.venv_path.exists():
                print_info("Removendo ambiente virtual existente...")
                shutil.rmtree(self.venv_path)

            print_info("Criando ambiente virtual...")
            venv.create(self.venv_path, with_pip=True)
            self.python_executable = self.get_venv_python()

            # Atualizar pip
            print_info("Atualizando pip...")
            self.run_venv_command(
                [self.python_executable, "-m", "pip", "install", "--upgrade", "pip"]
            )

        print_success(f"Ambiente Python configurado: {self.python_executable}")

    def get_venv_python(self) -> str:
        """Retorna o caminho do executável Python no venv"""
        if platform.system() == "Windows":
            return str(self.venv_path / "Scripts" / "python.exe")
        else:
            return str(self.venv_path / "bin" / "python")

    def run_venv_command(
        self, command: List[str], **kwargs
    ) -> subprocess.CompletedProcess:
        """Executa comando no ambiente virtual"""
        env = os.environ.copy()
        env["VIRTUAL_ENV"] = str(self.venv_path)
        env["PATH"] = f"{self.venv_path / 'bin'}:{env['PATH']}"
        return subprocess.run(command, env=env, **kwargs)

    def install_dependencies(self):
        """Instala dependências Python"""
        print_step("Instalando dependências Python")

        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            print_error("requirements.txt não encontrado")
            sys.exit(1)

        print_info("Instalando pacotes do requirements.txt...")
        try:
            result = self.run_venv_command(
                [
                    self.python_executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    str(requirements_file),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                print_error(f"Erro ao instalar dependências:\n{result.stderr}")
                sys.exit(1)

            print_success("Dependências Python instaladas")

        except subprocess.SubprocessError as e:
            print_error(f"Erro ao executar pip: {e}")
            sys.exit(1)

        # Verificar instalação dos pacotes principais
        self.verify_python_packages()

    def verify_python_packages(self):
        """Verifica se os pacotes principais estão instalados"""
        print_info("Verificando pacotes instalados...")

        missing_packages = []
        for package in self.required_packages:
            try:
                result = self.run_venv_command(
                    [
                        self.python_executable,
                        "-c",
                        f"import {package.replace('-', '_')}",
                    ],
                    capture_output=True,
                )

                if result.returncode == 0:
                    print_colored(f"  {package} ✓", Colors.GREEN)
                else:
                    missing_packages.append(package)
                    print_colored(f"  {package} ✗", Colors.RED)

            except Exception:
                missing_packages.append(package)
                print_colored(f"  {package} ✗", Colors.RED)

        if missing_packages:
            print_warning(f"Pacotes faltando: {', '.join(missing_packages)}")
            print_info("Tentando instalar pacotes faltando...")

            for package in missing_packages:
                try:
                    self.run_venv_command(
                        [self.python_executable, "-m", "pip", "install", package]
                    )
                    print_success(f"Instalado: {package}")
                except Exception as e:
                    print_warning(f"Não foi possível instalar {package}: {e}")

    def verify_project_structure(self):
        """Verifica estrutura do projeto"""
        print_step("Verificando estrutura do projeto")

        required_dirs = ["app", "tests", "config"]
        required_files = ["main.py", "requirements.txt"]

        for directory in required_dirs:
            dir_path = self.project_root / directory
            if dir_path.exists():
                print_success(f"Diretório {directory}/ ✓")
            else:
                print_error(f"Diretório {directory}/ não encontrado")
                sys.exit(1)

        for file in required_files:
            file_path = self.project_root / file
            if file_path.exists():
                print_success(f"Arquivo {file} ✓")
            else:
                print_warning(f"Arquivo {file} não encontrado")

        # Verificar se o módulo app pode ser importado
        try:
            result = self.run_venv_command(
                [self.python_executable, "-c", "import app; print('App module OK')"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                print_success("Módulo app importável ✓")
            else:
                print_error(f"Erro ao importar módulo app:\n{result.stderr}")
                # Adicionar PYTHONPATH
                self.setup_pythonpath()

        except Exception as e:
            print_error(f"Erro ao verificar módulo app: {e}")

    def setup_pythonpath(self):
        """Configura PYTHONPATH"""
        print_info("Configurando PYTHONPATH...")
        pythonpath = os.environ.get("PYTHONPATH", "")
        project_path = str(self.project_root)

        if project_path not in pythonpath:
            new_pythonpath = (
                f"{project_path}:{pythonpath}" if pythonpath else project_path
            )
            os.environ["PYTHONPATH"] = new_pythonpath
            print_success(f"PYTHONPATH configurado: {new_pythonpath}")

    def setup_frontend(self):
        """Configura frontend se necessário"""
        print_step("Configurando frontend")

        frontend_dir = self.project_root / "frontend"
        if not frontend_dir.exists():
            print_warning(
                "Diretório frontend/ não encontrado - pulando configuração frontend"
            )
            return

        # Verificar Node.js
        if not shutil.which("node"):
            print_warning("Node.js não encontrado - pulando configuração frontend")
            return

        if not shutil.which("npm"):
            print_warning("npm não encontrado - pulando configuração frontend")
            return

        # Verificar package.json
        package_json = frontend_dir / "package.json"
        if not package_json.exists():
            print_warning("package.json não encontrado - pulando configuração frontend")
            return

        # Instalar dependências do frontend
        node_modules = frontend_dir / "node_modules"
        if not node_modules.exists() or self.args.force_reinstall:
            print_info("Instalando dependências do frontend...")
            try:
                result = subprocess.run(
                    ["npm", "install"],
                    cwd=frontend_dir,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minutos
                )

                if result.returncode == 0:
                    print_success("Dependências do frontend instaladas")
                else:
                    print_warning(
                        f"Erro ao instalar dependências do frontend:\n{result.stderr}"
                    )

            except subprocess.TimeoutExpired:
                print_warning("Timeout ao instalar dependências do frontend")
            except subprocess.SubprocessError as e:
                print_warning(f"Erro ao executar npm: {e}")
        else:
            print_success("Dependências do frontend já instaladas")

    def check_external_services(self):
        """Verifica serviços externos necessários"""
        print_step("Verificando serviços externos")

        # Verificar conectividade de rede
        try:
            import urllib.request

            urllib.request.urlopen("http://google.com", timeout=5)
            print_success("Conectividade de rede ✓")
        except Exception:
            print_warning(
                "Sem conectividade de rede - algumas funcionalidades podem não funcionar"
            )

        # Verificar Docker daemon
        if shutil.which("docker"):
            try:
                result = subprocess.run(
                    ["docker", "ps"], capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    print_success("Docker daemon ativo ✓")
                else:
                    print_warning("Docker daemon não está rodando")
            except Exception:
                print_warning("Não foi possível verificar Docker daemon")

    def run_verification_tests(self):
        """Executa testes de verificação básicos"""
        print_step("Executando testes de verificação")

        # Teste de importação básica
        print_info("Testando importações básicas...")
        test_imports = [
            "app.agent.manus",
            "app.config",
            "app.logger",
            "app.llm",
            "fastapi",
            "uvicorn",
        ]

        for module in test_imports:
            try:
                result = self.run_venv_command(
                    [
                        self.python_executable,
                        "-c",
                        f"import {module}; print('{module} OK')",
                    ],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                )

                if result.returncode == 0:
                    print_colored(f"  {module} ✓", Colors.GREEN)
                else:
                    print_colored(f"  {module} ✗ - {result.stderr.strip()}", Colors.RED)

            except Exception as e:
                print_colored(f"  {module} ✗ - {e}", Colors.RED)

        # Teste básico do FastAPI
        print_info("Testando configuração do FastAPI...")
        try:
            test_code = """
import sys
sys.path.insert(0, '.')
from app.api.main import app
print('FastAPI app created successfully')
"""
            result = self.run_venv_command(
                [self.python_executable, "-c", test_code],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                print_success("FastAPI configurado corretamente ✓")
            else:
                print_warning(f"Problema com FastAPI: {result.stderr}")

        except Exception as e:
            print_warning(f"Não foi possível testar FastAPI: {e}")

    def start_system(self):
        """Inicia o sistema OpenManus"""
        print_step("Iniciando sistema OpenManus")

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        try:
            # Iniciar backend
            self.start_backend()

            # Aguardar backend inicializar
            time.sleep(3)

            # Verificar se backend está rodando
            if not self.check_backend_health():
                print_error("Backend não está respondendo")
                return

            # Iniciar frontend se necessário
            if not self.args.backend_only:
                self.start_frontend()

            # Mostrar informações de acesso
            self.show_access_info()

            # Aguardar serviços
            print_info("Pressione Ctrl+C para parar todos os serviços")
            self.wait_for_services()

        except Exception as e:
            print_error(f"Erro ao iniciar sistema: {e}")
            self.cleanup()

    def start_backend(self):
        """Inicia o backend FastAPI"""
        print_info("Iniciando backend FastAPI...")

        try:
            # Comando para iniciar uvicorn
            cmd = [
                self.python_executable,
                "-m",
                "uvicorn",
                "app.api.main:app",
                "--reload",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
            ]

            # Iniciar processo
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                env=self.get_env_with_pythonpath(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            self.services_pids["backend"] = process
            print_success(f"Backend iniciado (PID: {process.pid})")

        except Exception as e:
            print_error(f"Erro ao iniciar backend: {e}")
            raise

    def start_frontend(self):
        """Inicia o frontend"""
        frontend_dir = self.project_root / "frontend"
        if not frontend_dir.exists():
            print_warning("Frontend não encontrado")
            return

        if not shutil.which("npm"):
            print_warning("npm não encontrado - não é possível iniciar frontend")
            return

        print_info("Iniciando frontend...")

        try:
            # Verificar se há script dev
            package_json = frontend_dir / "package.json"
            if package_json.exists():
                with open(package_json) as f:
                    package_data = json.load(f)
                    scripts = package_data.get("scripts", {})

                    if "dev" in scripts:
                        cmd = ["npm", "run", "dev"]
                    elif "start" in scripts:
                        cmd = ["npm", "start"]
                    else:
                        print_warning(
                            "Script de desenvolvimento não encontrado no package.json"
                        )
                        return

                    # Iniciar processo
                    process = subprocess.Popen(
                        cmd,
                        cwd=frontend_dir,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                    )

                    self.services_pids["frontend"] = process
                    print_success(f"Frontend iniciado (PID: {process.pid})")

        except Exception as e:
            print_warning(f"Erro ao iniciar frontend: {e}")

    def check_backend_health(self) -> bool:
        """Verifica se o backend está respondendo"""
        try:
            import urllib.error
            import urllib.request

            for attempt in range(10):  # Tentar por 10 segundos
                try:
                    with urllib.request.urlopen(
                        "http://localhost:8000/health", timeout=2
                    ) as response:
                        if response.status == 200:
                            return True
                except urllib.error.URLError:
                    pass

                time.sleep(1)

            return False

        except Exception:
            return False

    def get_env_with_pythonpath(self) -> Dict[str, str]:
        """Retorna ambiente com PYTHONPATH configurado"""
        env = os.environ.copy()
        env["PYTHONPATH"] = str(self.project_root)
        env["VIRTUAL_ENV"] = str(self.venv_path)
        return env

    def show_access_info(self):
        """Mostra informações de acesso"""
        print_colored("\n" + "=" * 60, Colors.WHITE)
        print_colored("🎉 OpenManus iniciado com sucesso!", Colors.GREEN)
        print_colored("=" * 60, Colors.WHITE)

        print_colored("📍 URLs de Acesso:", Colors.BLUE)
        print_colored("  • Backend API: http://localhost:8000", Colors.CYAN)
        print_colored("  • Documentação API: http://localhost:8000/docs", Colors.CYAN)
        print_colored("  • Redoc: http://localhost:8000/redoc", Colors.CYAN)

        if "frontend" in self.services_pids:
            print_colored(
                "  • Frontend: http://localhost:3000 (ou próxima porta disponível)",
                Colors.CYAN,
            )

        print_colored("\n💡 Dicas:", Colors.YELLOW)
        print_colored("  • Use Ctrl+C para parar todos os serviços", Colors.WHITE)
        print_colored("  • Logs estão sendo salvos em logs/", Colors.WHITE)
        print_colored("  • Para debug, acesse http://localhost:8000/docs", Colors.WHITE)

        print_colored("\n" + "=" * 60, Colors.WHITE)

    def wait_for_services(self):
        """Aguarda pelos serviços"""
        try:
            while True:
                # Verificar se algum processo morreu
                dead_services = []
                for service, process in self.services_pids.items():
                    if process.poll() is not None:
                        dead_services.append(service)

                if dead_services:
                    print_warning(f"Serviços mortos: {', '.join(dead_services)}")
                    break

                time.sleep(1)

        except KeyboardInterrupt:
            pass

    def signal_handler(self, signum, frame):
        """Handler para sinais do sistema"""
        print_warning("\nRecebido sinal de interrupção")
        self.cleanup()
        sys.exit(0)

    def cleanup(self):
        """Limpa recursos e para serviços"""
        print_step("Parando serviços...")

        for service, process in self.services_pids.items():
            try:
                if process.poll() is None:  # Processo ainda está rodando
                    print_info(f"Parando {service} (PID: {process.pid})...")
                    process.terminate()

                    # Aguardar um pouco para terminar graciosamente
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        print_warning(f"Forçando parada do {service}...")
                        process.kill()
                        process.wait()

                    print_success(f"{service} parado")

            except Exception as e:
                print_warning(f"Erro ao parar {service}: {e}")

        print_success("Cleanup concluído")


def main():
    """Função principal"""
    parser = argparse.ArgumentParser(
        description="OpenManus - Setup e Inicialização Automática",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python setup_and_run.py                    # Setup completo e inicialização
  python setup_and_run.py --backend-only     # Apenas backend
  python setup_and_run.py --skip-tests       # Pula verificações
  python setup_and_run.py --force-reinstall  # Força reinstalação
        """,
    )

    parser.add_argument(
        "--backend-only",
        action="store_true",
        help="Executa apenas o backend (sem frontend)",
    )

    parser.add_argument(
        "--skip-tests", action="store_true", help="Pula os testes de verificação"
    )

    parser.add_argument(
        "--force-reinstall",
        action="store_true",
        help="Força reinstalação das dependências",
    )

    args = parser.parse_args()

    # Criar e executar setup
    setup = OpenManusSetup(args)
    setup.run()


if __name__ == "__main__":
    main()
