import ast
from io import StringIO
import logging
import sys
from typing import Any

logger = logging.getLogger(__name__)


def validate_code_safety(code: str) -> tuple[bool, str]:
    """Validate Python code for dangerous operations."""
    try:
        tree = ast.parse(code)
        dangerous_imports = {"os", "subprocess", "sys", "importlib", "__import__"}
        dangerous_functions = {"eval", "exec", "compile", "open"}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    if name.name in dangerous_imports:
                        return False, f"Dangerous import detected: {name.name}"
            elif isinstance(node, ast.ImportFrom):
                if node.module in dangerous_imports:
                    return False, f"Dangerous import detected: {node.module}"
            elif isinstance(node, ast.Call) and (
                isinstance(node.func, ast.Name) and node.func.id in dangerous_functions
            ):
                return False, f"Dangerous function detected: {node.func.id}"
        return True, ""
    except SyntaxError as e:
        return False, f"Syntax error: {e!s}"


def execute_python_code(code: str, timeout: int = 10) -> dict[str, Any]:  # noqa: ARG001
    """Execute Python code with security restrictions."""
    result_dict: dict[str, Any] = {}

    # Validate code safety
    is_safe, error_msg = validate_code_safety(code)
    if not is_safe:
        result_dict["observation"] = f"Security Error: {error_msg}"
        return result_dict

    # Create restricted globals
    safe_globals = {
        "__builtins__": {
            "print": print,
            "len": len,
            "range": range,
            "str": str,
            "int": int,
            "float": float,
            "list": list,
            "dict": dict,
            "tuple": tuple,
            "set": set,
            "bool": bool,
            "abs": abs,
            "max": max,
            "min": min,
            "sum": sum,
            "sorted": sorted,
            "reversed": reversed,
            "enumerate": enumerate,
            "zip": zip,
        }
    }

    # Capture output
    output_buffer = StringIO()
    original_stdout = sys.stdout

    try:
        sys.stdout = output_buffer

        # Compile and execute with restrictions
        compiled_code = compile(code, "<string>", "exec")
        exec(compiled_code, safe_globals, safe_globals)  # nosec # Execute sandboxed code
        result_dict["observation"] = output_buffer.getvalue()

    except Exception as e:
        result_dict["observation"] = f"Execution Error: {e!s}"
        logger.error(f"Code execution failed: {e}")
    finally:
        sys.stdout = original_stdout

    return result_dict
