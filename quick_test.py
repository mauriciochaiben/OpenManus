#!/usr/bin/env python3
"""
OpenManus - Teste Rápido do Sistema
====================================

Script simples para testar se o sistema OpenManus está funcionando corretamente.
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import requests


def print_status(message, status="info"):
    """Print com cores e símbolos"""
    colors = {
        "info": "\033[0;34m",  # Azul
        "success": "\033[0;32m",  # Verde
        "warning": "\033[1;33m",  # Amarelo
        "error": "\033[0;31m",  # Vermelho
        "reset": "\033[0m",  # Reset
    }

    symbols = {"info": "ℹ️ ", "success": "✅", "warning": "⚠️ ", "error": "❌"}

    color = colors.get(status, colors["info"])
    symbol = symbols.get(status, "")
    reset = colors["reset"]

    print(f"{color}{symbol} {message}{reset}")


def test_environment():
    """Testa o ambiente básico"""
    print_status("Testando ambiente básico...", "info")

    # Verifica Python
    python_version = sys.version_info
    if python_version >= (3, 8):
        print_status(
            f"Python {python_version.major}.{python_version.minor}.{python_version.micro} ✓",
            "success",
        )
    else:
        print_status(
            f"Python {python_version.major}.{python_version.minor} é muito antigo (necessário 3.8+)",
            "error",
        )
        return False

    # Verifica diretório de trabalho
    if not Path("main.py").exists():
        print_status(
            "Arquivo main.py não encontrado. Execute este script no diretório raiz do OpenManus",
            "error",
        )
        return False

    print_status("Arquivo main.py encontrado ✓", "success")

    # Verifica virtual environment
    venv_path = Path(".venv")
    if venv_path.exists():
        print_status("Virtual environment encontrado ✓", "success")
    else:
        print_status("Virtual environment não encontrado", "warning")

    return True


def test_imports():
    """Testa imports básicos"""
    print_status("Testando imports essenciais...", "info")

    try:
        import importlib.util

        if importlib.util.find_spec("fastapi") is not None:
            print_status("FastAPI ✓", "success")
        else:
            raise ImportError("FastAPI not found")
    except ImportError:
        print_status("FastAPI não instalado", "error")
        return False

    try:
        import importlib.util

        if importlib.util.find_spec("uvicorn") is not None:
            print_status("Uvicorn ✓", "success")
        else:
            raise ImportError("Uvicorn not found")
    except ImportError:
        print_status("Uvicorn não instalado", "error")
        return False

    try:
        # Adiciona o diretório atual ao Python path
        import sys

        if "." not in sys.path:
            sys.path.insert(0, ".")

        import importlib.util

        if importlib.util.find_spec("app.api.main") is not None:
            print_status("App principal ✓", "success")
        else:
            raise ImportError("App principal not found")
    except ImportError as e:
        print_status(f"Erro ao importar app principal: {e}", "error")
        return False

    return True


def start_backend():
    """Inicia o backend"""
    print_status("Iniciando backend...", "info")

    # Configura o ambiente
    env = os.environ.copy()
    if Path(".venv").exists():
        venv_python = Path(".venv/bin/python").absolute()
        if venv_python.exists():
            env["PATH"] = f"{venv_python.parent}:{env.get('PATH', '')}"

    # Inicia o backend
    try:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.api.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--reload",
            ],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        print_status(f"Backend iniciado (PID: {process.pid})", "success")
        return process
    except Exception as e:
        print_status(f"Erro ao iniciar backend: {e}", "error")
        return None


def test_backend():
    """Testa se o backend está funcionando"""
    print_status("Testando backend...", "info")

    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                data = response.json()
                print_status(f"Backend respondendo: {data}", "success")
                return True
        except requests.exceptions.RequestException:
            pass

        if attempt < max_attempts - 1:
            time.sleep(1)

    print_status("Backend não está respondendo", "error")
    return False


def main():
    """Função principal"""
    print("🚀 OpenManus - Teste Rápido do Sistema")
    print("=" * 50)

    # Testa ambiente
    if not test_environment():
        sys.exit(1)

    # Testa imports
    if not test_imports():
        print_status("Execute: pip install -r requirements.txt", "warning")
        sys.exit(1)

    # Inicia backend
    backend_process = start_backend()
    if not backend_process:
        sys.exit(1)

    try:
        # Aguarda um pouco para o backend inicializar
        time.sleep(3)

        # Testa backend
        if test_backend():
            print_status("Sistema OpenManus funcionando corretamente! 🎉", "success")
            print_status("Backend disponível em: http://localhost:8000", "info")
            print_status("Pressione Ctrl+C para parar", "info")

            # Mantém o processo rodando
            try:
                backend_process.wait()
            except KeyboardInterrupt:
                print_status("Parando sistema...", "info")
        else:
            print_status("Sistema com problemas", "error")

    finally:
        # Para o backend
        if backend_process:
            backend_process.terminate()
            backend_process.wait()
            print_status("Backend parado", "info")


if __name__ == "__main__":
    main()
