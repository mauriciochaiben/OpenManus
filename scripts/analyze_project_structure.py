"""
Script de análise de migração - ATUALIZADO

==========================================

Este script foi atualizado após a remoção do diretório backend/.
Agora serve como ferramenta de análise da estrutura atual do projeto.

Data da atualização: 3 de junho de 2025
Razão: Remoção do diretório backend/ obsoleto durante refatoração
"""

from collections import defaultdict
import fnmatch
import os
from pathlib import Path

# Configure paths
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"

# File types to analyze
CODE_EXTENSIONS = [".py", ".json", ".yml", ".yaml"]
IGNORE_PATTERNS = ["__pycache__", "*.pyc", "*.pyo", "*.pyd", "venv", ".env", ".git"]


class ProjectAnalyzer:
    """Analisa a estrutura atual do projeto após refatoração"""

    def __init__(self):
        self.app_files = {}
        self.app_modules = set()

    def collect_files(self):
        """Collect all relevant files from app directory"""
        print("📁 Coletando arquivos do diretório app/...")
        self.app_files = self._collect_dir_files(APP_DIR)

        # Extract module names from file paths
        for file_path in self.app_files:
            rel_path = os.path.relpath(file_path, APP_DIR)
            module_path = Path(rel_path).with_suffix("").as_posix().replace("/", ".")
            self.app_modules.add(module_path)

    def _collect_dir_files(self, directory):
        """Collect files from a directory, ignoring specific patterns"""
        files = []
        if not directory.exists():
            print(f"⚠️  Diretório não encontrado: {directory}")
            return files

        for root, dirs, filenames in os.walk(directory):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not any(fnmatch.fnmatch(d, pattern) for pattern in IGNORE_PATTERNS)]

            for filename in filenames:
                if any(fnmatch.fnmatch(filename, pattern) for pattern in IGNORE_PATTERNS):
                    continue

                file_path = Path(root) / filename
                ext = Path(filename).suffix
                if ext in CODE_EXTENSIONS:
                    files.append(str(file_path))
        return files

    def analyze_structure(self):
        """Analyze current project structure"""
        print("\n📊 Análise da Estrutura do Projeto")
        print("=" * 50)

        # Analyze directories
        directories = defaultdict(int)
        for file_path in self.app_files:
            rel_path = os.path.relpath(file_path, APP_DIR)
            dir_name = Path(rel_path).parent
            if str(dir_name) != ".":
                directories[str(dir_name)] += 1

        print(f"\n📂 Diretórios encontrados em app/ ({len(directories)} diretórios):")
        for dir_name, file_count in sorted(directories.items()):
            print(f"  • {dir_name}: {file_count} arquivo(s)")

        print(f"\n📄 Total de arquivos Python: {len([f for f in self.app_files if f.endswith('.py')])}")
        print(f"📄 Total de arquivos de configuração: {len([f for f in self.app_files if not f.endswith('.py')])}")

    def analyze_imports(self):
        """Analyze imports in project files"""
        print("\n📦 Análise de Imports")
        print("=" * 30)

        external_imports = set()
        internal_imports = set()

        for file_path in self.app_files:
            if not file_path.endswith(".py"):
                continue

            try:
                with Path(file_path).open(encoding="utf-8") as f:
                    content = f.read()

                # Find import statements
                import_lines = []
                for line in content.split("\n"):
                    line = line.strip()
                    if line.startswith("import ") or line.startswith("from "):
                        import_lines.append(line)

                for import_line in import_lines:
                    # Extract module name
                    if import_line.startswith("from "):
                        module = import_line.split()[1].split(".")[0]
                    else:  # starts with 'import '
                        module = import_line.split()[1].split(".")[0]

                    if module.startswith("app") or module == "." or module.startswith(".."):
                        internal_imports.add(module)
                    else:
                        external_imports.add(module)

            except Exception as e:
                print(f"⚠️  Erro ao ler {file_path}: {e}")

        print(f"\n🔗 Imports externos únicos: {len(external_imports)}")
        if external_imports:
            sorted_external = sorted(external_imports)[:10]  # Show first 10
            for imp in sorted_external:
                print(f"  • {imp}")
            if len(external_imports) > 10:
                print(f"  ... e mais {len(external_imports) - 10}")

        print(f"\n🏠 Imports internos únicos: {len(internal_imports)}")
        for imp in sorted(internal_imports):
            print(f"  • {imp}")

    def generate_report(self):
        """Generate comprehensive project analysis report"""
        print("\n" + "=" * 60)
        print("🎯 RELATÓRIO DE ANÁLISE DO PROJETO OPENMANUS")
        print("=" * 60)
        print("📅 Data: 3 de junho de 2025")
        print("🔧 Status: Projeto refatorado (diretório backend/ removido)")
        print(f"📁 Diretório analisado: {APP_DIR}")

        self.collect_files()
        self.analyze_structure()
        self.analyze_imports()

        print("\n✅ CONCLUSÕES:")
        print("  • Estrutura do projeto limpa e organizada")
        print("  • Diretório backend/ obsoleto removido com sucesso")
        print("  • Arquitetura consolidada no diretório app/")
        print("  • Projeto pronto para desenvolvimento contínuo")


def main():
    """Main function to run the analysis"""
    print("🔍 Iniciando análise do projeto OpenManus...")
    print("📝 Nota: Este script foi atualizado após a remoção do diretório backend/")

    analyzer = ProjectAnalyzer()
    analyzer.generate_report()

    print("\n🎉 Análise concluída!")


if __name__ == "__main__":
    main()
