#!/usr/bin/env python3
"""
Script to fix remaining RUF012 ClassVar issues in tool files.
"""

from pathlib import Path
import re


def fix_classvar_issues():
    """Fix ClassVar annotation issues in tool files."""
    # Files that need ClassVar fixes
    tool_files = [
        "app/tool/chart_visualization/chart_prepare.py",
        "app/tool/chart_visualization/data_visualization.py",
        "app/tool/chart_visualization/python_execute.py",
        "app/tool/coordination.py",
        "app/tool/create_chat_completion.py",
        "app/tool/document_analyzer.py",
        "app/tool/document_reader.py",
        "app/tool/mcp.py",
        "app/tool/planning.py",
        "app/tool/str_replace_editor.py",
        "app/tool/terminate.py",
        "app/tool/tool_executor_service.py",
        "app/tool/web_search.py",
    ]

    for file_path in tool_files:
        full_path = Path(file_path)
        if not full_path.exists():
            continue

        print(f"Processing {file_path}...")

        # Read file
        content = full_path.read_text()

        # Add ClassVar import if not present
        if "from typing import" in content and "ClassVar" not in content:
            content = re.sub(r"(from typing import [^)]+)", r"\1, ClassVar", content)
        elif "from typing import" not in content and "import typing" not in content:
            # Add import if no typing import exists
            lines = content.split("\n")
            import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    import_idx = i + 1
            lines.insert(import_idx, "from typing import ClassVar")
            content = "\n".join(lines)

        # Fix parameters: dict = { patterns
        content = re.sub(r"(\s+parameters):\s*dict\s*=\s*{", r"\1: ClassVar[dict] = {", content)

        # Fix other mutable class attributes
        patterns = [
            (
                r"(\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*dict\s*=\s*{",
                r"\1\2: ClassVar[dict] = {",
            ),
            (
                r"(\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*dict\[([^\]]+)\]\s*=\s*{",
                r"\1\2: ClassVar[dict[\3]] = {",
            ),
            (
                r"(\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*set\s*=\s*{",
                r"\1\2: ClassVar[set] = {",
            ),
            (
                r"(\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*:\s*list\s*=\s*\[",
                r"\1\2: ClassVar[list] = [",
            ),
            (
                r"(\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*{([^}]+)}\s*#",
                r"\1\2: ClassVar = {\3} #",
            ),
            (
                r"(\s+)([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*defaultdict\(",
                r"\1\2: ClassVar = defaultdict(",
            ),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        # Write back
        full_path.write_text(content)
        print(f"  ✅ Fixed {file_path}")


if __name__ == "__main__":
    fix_classvar_issues()
    print("ClassVar fixes completed!")
