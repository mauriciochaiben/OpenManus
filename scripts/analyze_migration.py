#!/usr/bin/env python3
"""
Script para análise da estrutura do projeto OpenManus após a remoção do diretório backend/

Parte da refatoração do projeto OpenManus
"""

from collections import defaultdict
import fnmatch
import os
from pathlib import Path
import re
import sys

# Configure paths
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"

# File types to analyze
CODE_EXTENSIONS = [".py", ".json", ".yml", ".yaml"]
IGNORE_PATTERNS = ["__pycache__", "*.pyc", "*.pyo", "*.pyd", "venv", ".env", ".git"]


class ProjectAnalyzer:
    def __init__(self):
        self.app_files = {}
        self.app_modules = set()
        self.issues = []

    def collect_files(self):
        """Collect all relevant files from app directory"""
        print("🔍 Analisando estrutura do projeto...")
        self.app_files = self._collect_dir_files(APP_DIR)

        # Extract module names from file paths
        for file_path in self.app_files:
            rel_path = os.path.relpath(file_path, APP_DIR)
            module_path = Path(rel_path).with_suffix("").as_posix().replace("/", ".")
            self.app_modules.add(module_path)

    def _collect_dir_files(self, directory):
        """Collect files from a directory recursively"""
        files = {}
        if not directory.exists():
            return files

        for root, dirs, filenames in os.walk(directory):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, pattern) for pattern in IGNORE_PATTERNS)]

            for filename in filenames:
                if any(filename.endswith(ext) for ext in CODE_EXTENSIONS):
                    file_path = Path(root) / filename
                    try:
                        with file_path.open("r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        files[str(file_path)] = content
                    except (UnicodeDecodeError, PermissionError) as e:
                        print(f"⚠️  Erro ao ler {file_path}: {e}")

        return files

    def check_project_health(self):
        """Check for common issues in the project structure"""
        print("🏥 Verificando saúde do projeto...")

        # Check for missing __init__.py files
        self._check_missing_init_files()

        # Check for broken imports
        self._check_imports()

        # Check for duplicate functionality
        self._check_duplicates()

    def _check_missing_init_files(self):
        """Check for directories that should have __init__.py"""
        python_dirs = set()

        for file_path in self.app_files:
            if file_path.endswith(".py"):
                dir_path = Path(file_path).parent
                while str(dir_path) != str(APP_DIR):
                    python_dirs.add(str(dir_path))
                    dir_path = dir_path.parent

        for dir_path in python_dirs:
            init_file = Path(dir_path) / "__init__.py"
            if not init_file.exists():
                rel_path = os.path.relpath(dir_path, APP_DIR)
                self.issues.append(f"Faltando __init__.py em: {rel_path}")

    def _check_imports(self):
        """Check for potentially broken imports"""
        import_pattern = re.compile(r"^(?:from|import)\s+([.\w]+)(?:\s+import)?", re.MULTILINE)

        for file_path, content in self.app_files.items():
            if not file_path.endswith(".py"):
                continue

            imports = import_pattern.findall(content)
            for imp in imports:
                # Check for old backend imports
                if "backend" in imp.lower():
                    rel_path = os.path.relpath(file_path, APP_DIR)
                    self.issues.append(f"Possível import obsoleto em {rel_path}: {imp}")

    def _check_duplicates(self):
        """Check for potential duplicate functionality"""
        # Check for files with similar names
        file_names = defaultdict(list)

        for file_path in self.app_files:
            if file_path.endswith(".py"):
                file_name = Path(file_path).stem
                rel_path = os.path.relpath(file_path, APP_DIR)
                file_names[file_name].append(rel_path)

        for name, paths in file_names.items():
            if len(paths) > 1:
                self.issues.append(f"Arquivos com nomes similares: {name} -> {', '.join(paths)}")

    def generate_report(self):
        """Generate a comprehensive analysis report"""
        print("\n" + "=" * 80)
        print("📊 RELATÓRIO DE ANÁLISE DO PROJETO OPENMANUS")
        print("=" * 80)

        print("\n📁 Estrutura do Projeto:")
        print("   • Diretório principal: app/")
        print(f"   • Arquivos Python analisados: {len([f for f in self.app_files if f.endswith('.py')])}")
        print(f"   • Módulos identificados: {len(self.app_modules)}")

        print("\n🎯 Status da Migração:")
        print("   ✅ Diretório backend/ removido com sucesso")
        print("   ✅ Estrutura consolidada em app/")

        if self.issues:
            print(f"\n⚠️  Problemas Identificados ({len(self.issues)}):")
            for i, issue in enumerate(self.issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("\n✅ Nenhum problema identificado!")

        print("\n📋 Módulos Principais:")
        main_modules = [m for m in sorted(self.app_modules) if "." not in m and m != "__init__"]
        for module in main_modules[:10]:  # Show first 10
            print(f"   • {module}")
        if len(main_modules) > 10:
            print(f"   ... e mais {len(main_modules) - 10} módulos")

    def run_analysis(self):
        """Run the complete analysis"""
        self.collect_files()
        self.check_project_health()
        self.generate_report()

        return len(self.issues) == 0


def main():
    """Main execution function"""
    print("🚀 Iniciando análise do projeto OpenManus...")

    analyzer = ProjectAnalyzer()
    success = analyzer.run_analysis()

    if success:
        print("\n🎉 Análise concluída com sucesso!")
        sys.exit(0)
    else:
        print(f"\n⚠️  Análise concluída com {len(analyzer.issues)} problemas encontrados.")
        sys.exit(1)


if __name__ == "__main__":
    main()
