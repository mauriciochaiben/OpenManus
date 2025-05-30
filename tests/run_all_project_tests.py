#!/usr/bin/env python3
"""
Script para executar todos os testes do OpenManus
Executa testes de backend (Python) e frontend (JavaScript/TypeScript)
"""

import os
import subprocess
import sys
from pathlib import Path

# Cores para a saída
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
ENDC = "\033[0m"
BOLD = "\033[1m"


def print_header(title):
    """Exibe um cabeçalho formatado"""
    print(f"\n{BLUE}{'=' * 50}{ENDC}")
    print(f"{BOLD}{BLUE}{title}{ENDC}")
    print(f"{BLUE}{'=' * 50}{ENDC}\n")


def run_backend_tests():
    """Executa todos os testes do backend"""
    print_header("EXECUTANDO TESTES DO BACKEND")

    # Path do diretório atual do script
    current_dir = Path(__file__).parent.absolute()

    # Path do script run_all_tests.py
    run_all_tests_path = current_dir / "run_all_tests.py"

    # Execute o script Python para testes do backend
    result = subprocess.run(
        [sys.executable, str(run_all_tests_path)], capture_output=True, text=True
    )

    print(result.stdout)

    if result.returncode != 0:
        print(f"{RED}Testes do backend falharam com código {result.returncode}{ENDC}")
        print(result.stderr)
        return False

    return True


def run_frontend_tests():
    """Executa todos os testes do frontend"""
    print_header("EXECUTANDO TESTES DO FRONTEND")

    # Path do diretório do frontend
    frontend_dir = Path(__file__).parent.parent / "frontend"

    # Verificar se o diretório existe
    if not frontend_dir.exists():
        print(f"{RED}Diretório do frontend não encontrado: {frontend_dir}{ENDC}")
        return False

    # Execute 'npm test' no diretório do frontend
    os.chdir(frontend_dir)
    result = subprocess.run(["npm", "test"], capture_output=True, text=True)

    print(result.stdout)

    if result.returncode != 0:
        print(f"{RED}Testes do frontend falharam com código {result.returncode}{ENDC}")
        print(result.stderr)
        return False

    return True


def main():
    """Função principal que executa todos os testes"""
    print(f"{BOLD}{YELLOW}🧪 INICIANDO TESTES COMPLETOS DO OPENMANUS{ENDC}\n")

    backend_success = run_backend_tests()
    frontend_success = run_frontend_tests()

    # Mostrar resumo final
    print_header("RESUMO DOS TESTES")

    print(
        f"Backend: {GREEN}✅ PASSOU{ENDC}"
        if backend_success
        else f"Backend: {RED}❌ FALHOU{ENDC}"
    )
    print(
        f"Frontend: {GREEN}✅ PASSOU{ENDC}"
        if frontend_success
        else f"Frontend: {RED}❌ FALHOU{ENDC}"
    )

    all_passed = backend_success and frontend_success

    if all_passed:
        print(f"\n{GREEN}{BOLD}🎉 TODOS OS TESTES PASSARAM!{ENDC}")
        return 0
    else:
        print(f"\n{RED}{BOLD}❌ ALGUNS TESTES FALHARAM!{ENDC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
