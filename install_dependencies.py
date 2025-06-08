#!/usr/bin/env python3
"""
OpenManus Modular Installation Script

Permite instalar apenas as dependências necessárias para as funcionalidades desejadas.

Uso:
    python install_dependencies.py [opções]

Opções:
    --core              Instala apenas dependências essenciais
    --features          Adiciona funcionalidades avançadas
    --documents         Adiciona processamento de documentos
    --search            Adiciona motores de busca
    --browser           Adiciona automação de browser
    --all               Instala tudo (equivale ao requirements.txt original)
    --list              Lista módulos disponíveis
    --dry-run           Mostra o que seria instalado sem instalar
"""

import argparse
from pathlib import Path
import subprocess
import sys


class ModularInstaller:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.modules = {
            "core": {
                "file": "requirements-core.txt",
                "description": "Dependências essenciais (FastAPI, OpenAI, etc.)",
                "dependencies": 19,
            },
            "features": {
                "file": "requirements-features.txt",
                "description": "Funcionalidades avançadas (embeddings, sandbox, etc.)",
                "dependencies": 10,
            },
            "documents": {
                "file": "requirements-documents.txt",
                "description": "Processamento avançado de documentos",
                "dependencies": 6,
            },
            "search": {
                "file": "requirements-search.txt",
                "description": "Motores de busca (Google, Baidu, DuckDuckGo)",
                "dependencies": 3,
            },
            "browser": {
                "file": "requirements-browser.txt",
                "description": "Automação de browser",
                "dependencies": 1,
            },
        }

    def list_modules(self):
        """Lista todos os módulos disponíveis."""
        print("📦 Módulos disponíveis:")
        print("=" * 50)

        total_deps = 0
        for name, info in self.modules.items():
            print(f"🔹 {name.upper()}")
            print(f"   Descrição: {info['description']}")
            print(f"   Dependências: {info['dependencies']}")
            print(f"   Arquivo: {info['file']}")
            print()
            total_deps += info["dependencies"]

        print(f"Total máximo de dependências: {total_deps}")
        print("\nVs. requirements.txt original: 71 dependências")
        reduction = ((71 - total_deps) / 71) * 100
        print(f"Redução potencial: {71 - total_deps} dependências ({reduction:.1f}%)")

    def validate_modules(self, modules):
        """Valida se os módulos existem."""
        invalid = []
        for module in modules:
            if module not in self.modules:
                invalid.append(module)

        if invalid:
            print(f"❌ Módulos inválidos: {', '.join(invalid)}")
            print("Use --list para ver módulos disponíveis")
            sys.exit(1)

    def get_requirements_files(self, modules):
        """Retorna lista de arquivos de requirements para os módulos."""
        files = []
        for module in modules:
            file_path = self.project_root / self.modules[module]["file"]
            if file_path.exists():
                files.append(file_path)
            else:
                print(f"⚠️  Arquivo não encontrado: {file_path}")

        return files

    def install_modules(self, modules, dry_run=False):
        """Instala os módulos especificados."""
        if not modules:
            print("❌ Nenhum módulo especificado")
            return

        self.validate_modules(modules)
        files = self.get_requirements_files(modules)

        if not files:
            print("❌ Nenhum arquivo de requirements encontrado")
            return

        print("🚀 Instalação Modular OpenManus")
        print("=" * 40)
        print(f"Módulos selecionados: {', '.join(modules)}")

        total_deps = sum(self.modules[m]["dependencies"] for m in modules)
        print(f"Total de dependências: {total_deps}")
        print()

        for module in modules:
            info = self.modules[module]
            print(f"📋 {module.upper()}: {info['description']}")

        print()

        if dry_run:
            print("🔍 DRY RUN - Comandos que seriam executados:")
            for file_path in files:
                print(f"   pip install -r {file_path}")
            return

        # Instalar cada arquivo de requirements
        for file_path in files:
            print(f"📦 Instalando {file_path.name}...")
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", str(file_path)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                print(f"✅ {file_path.name} instalado com sucesso")
            except subprocess.CalledProcessError as e:
                print(f"❌ Erro ao instalar {file_path.name}:")
                print(e.stderr)
                return

        print("\n🎉 Instalação concluída!")
        print(f"Dependências instaladas: {total_deps}")
        print(f"Economia vs. requirements.txt: {71 - total_deps} dependências")

    def install_all(self, dry_run=False):
        """Instala todas as dependências (equivale ao requirements.txt original)."""
        all_modules = list(self.modules.keys())
        print("🔥 Instalação COMPLETA - Todas as funcionalidades")
        self.install_modules(all_modules, dry_run)


def main():
    parser = argparse.ArgumentParser(
        description="OpenManus Modular Installation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
    python install_dependencies.py --core
    python install_dependencies.py --core --features
    python install_dependencies.py --core --documents --search
    python install_dependencies.py --all
    python install_dependencies.py --list
        """,
    )

    parser.add_argument("--core", action="store_true", help="Instalar dependências essenciais")
    parser.add_argument("--features", action="store_true", help="Instalar funcionalidades avançadas")
    parser.add_argument("--documents", action="store_true", help="Instalar processamento de documentos")
    parser.add_argument("--search", action="store_true", help="Instalar motores de busca")
    parser.add_argument("--browser", action="store_true", help="Instalar automação de browser")
    parser.add_argument("--all", action="store_true", help="Instalar tudo")
    parser.add_argument("--list", action="store_true", help="Listar módulos disponíveis")
    parser.add_argument("--dry-run", action="store_true", help="Mostrar o que seria instalado")

    args = parser.parse_args()

    installer = ModularInstaller()

    if args.list:
        installer.list_modules()
        return

    if args.all:
        installer.install_all(args.dry_run)
        return

    # Determinar módulos a instalar
    modules = []
    if args.core:
        modules.append("core")
    if args.features:
        modules.append("features")
    if args.documents:
        modules.append("documents")
    if args.search:
        modules.append("search")
    if args.browser:
        modules.append("browser")

    if not modules:
        print("❌ Nenhum módulo especificado!")
        print("Use --help para ver as opções disponíveis")
        print("Use --list para ver módulos disponíveis")
        return

    installer.install_modules(modules, args.dry_run)


if __name__ == "__main__":
    main()
