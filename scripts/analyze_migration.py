import fnmatch
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

# Configure paths
BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
BACKEND_DIR = BASE_DIR / "backend"

# File types to analyze
CODE_EXTENSIONS = [".py", ".json", ".yml", ".yaml"]
IGNORE_PATTERNS = ["__pycache__", "*.pyc", "*.pyo", "*.pyd", "venv", ".env", ".git"]


class MigrationAnalyzer:
    def __init__(self):
        self.app_files = {}
        self.backend_files = {}
        self.app_modules = set()
        self.backend_modules = set()
        self.unique_backend_files = []
        self.potential_migrations = []

    def collect_files(self):
        """Collect all relevant files from both directories"""
        print("Collecting files...")
        self.app_files = self._collect_dir_files(APP_DIR)
        self.backend_files = self._collect_dir_files(BACKEND_DIR)

        # Extract module names from file paths
        for file_path in self.app_files:
            rel_path = os.path.relpath(file_path, APP_DIR)
            module_path = Path(rel_path).with_suffix("").as_posix().replace("/", ".")
            self.app_modules.add(module_path)

        for file_path in self.backend_files:
            rel_path = os.path.relpath(file_path, BACKEND_DIR)
            module_path = Path(rel_path).with_suffix("").as_posix().replace("/", ".")
            self.backend_modules.add(module_path)

    def _collect_dir_files(self, directory):
        """Collect files from a directory, ignoring specific patterns"""
        files = []
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

    def find_unique_backend_files(self):
        """Find files in backend that don't exist in app"""
        print("Finding unique backend files...")

        # Compare file paths relatively
        app_rel_paths = {os.path.relpath(f, APP_DIR) for f in self.app_files}

        for backend_file in self.backend_files:
            rel_path = os.path.relpath(backend_file, BACKEND_DIR)

            # Check if this file exists in app directory
            if rel_path not in app_rel_paths:
                self.unique_backend_files.append(backend_file)

    def analyze_imports(self):
        """Analyze imports in backend files to find unique modules"""
        print("Analyzing imports...")

        backend_imports = defaultdict(set)

        # Extract imports from backend files
        for file_path in self.backend_files:
            with Path(file_path).open(encoding="utf-8", errors="ignore") as f:
                try:
                    content = f.read()
                    # Find import statements
                    import_lines = re.findall(
                        r"^(?:from|import)\s+([.\w]+)(?:\s+import)?",
                        content,
                        re.MULTILINE,
                    )

                    rel_path = os.path.relpath(file_path, BACKEND_DIR)
                    for import_module in import_lines:
                        if import_module.startswith("."):  # Relative import
                            # Skip standard library relative imports
                            continue

                        backend_imports[rel_path].add(import_module)
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")

        # Check if imported modules exist in app
        for file_path, imports in backend_imports.items():
            missing_modules = set()

            for imp in imports:
                # Filter out standard library imports and external packages
                if imp.split(".")[0] in sys.modules or "." not in imp:
                    continue

                # Check if this is a project-specific import
                if any(imp.startswith(mod) for mod in self.backend_modules) and not any(
                    imp.startswith(mod) for mod in self.app_modules
                ):
                    missing_modules.add(imp)

            if missing_modules:
                backend_file = BACKEND_DIR / file_path
                self.potential_migrations.append((str(backend_file), missing_modules))

    def analyze_content(self):
        """Analyze file content to find functional differences"""
        print("Analyzing file content...")

        for backend_file in self.backend_files:
            rel_path = os.path.relpath(backend_file, BACKEND_DIR)
            app_file = APP_DIR / rel_path

            # Skip if file doesn't exist in app directory
            if not Path(app_file).exists():
                continue

            try:
                # Compare file content
                with Path(backend_file).open(encoding="utf-8", errors="ignore") as f1:
                    backend_content = f1.read()
                with Path(app_file).open(encoding="utf-8", errors="ignore") as f2:
                    app_content = f2.read()

                # Extract function/class definitions
                backend_defs = re.findall(r"^\s*(def|class)\s+([^\(:]+)", backend_content, re.MULTILINE)
                app_defs = re.findall(r"^\s*(def|class)\s+([^\(:]+)", app_content, re.MULTILINE)

                backend_defs_set = {name.strip() for _, name in backend_defs}
                app_defs_set = {name.strip() for _, name in app_defs}

                # Find definitions in backend that don't exist in app
                unique_defs = backend_defs_set - app_defs_set

                if unique_defs:
                    self.potential_migrations.append((backend_file, unique_defs))
            except Exception as e:
                print(f"Error comparing {backend_file} and {app_file}: {e}")

    def generate_report(self):
        """Generate a report of files that need migration"""
        print("\n" + "=" * 80)
        print("MIGRATION ANALYSIS REPORT")
        print("=" * 80)

        print("\n1. Unique files in backend/ (not present in app/):")
        print("-" * 80)
        for file_path in sorted(self.unique_backend_files):
            rel_path = os.path.relpath(file_path, BACKEND_DIR)
            print(f"  - {rel_path}")

        print("\n2. Files with potential unique functionality to migrate:")
        print("-" * 80)
        for file_path, unique_items in sorted(self.potential_migrations):
            rel_path = os.path.relpath(file_path, BACKEND_DIR)
            print(f"  - {rel_path}")
            for item in sorted(unique_items):
                print(f"      * {item}")

        print("\nRECOMMENDATION:")
        print("-" * 80)
        print("The above files should be manually inspected before removing the backend/ directory.")
        print("They may contain functionality that needs to be migrated to the app/ directory.")
        print("=" * 80)


if __name__ == "__main__":
    analyzer = MigrationAnalyzer()
    analyzer.collect_files()
    analyzer.find_unique_backend_files()
    analyzer.analyze_imports()
    analyzer.analyze_content()
    analyzer.generate_report()
