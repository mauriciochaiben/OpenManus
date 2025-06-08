"""
Code Execution Tool

Secure code execution tool supporting multiple programming languages.
Uses restrictedpython for Python and subprocess for other languages with security measures.
"""

from contextlib import redirect_stderr, redirect_stdout, suppress
from io import StringIO
import logging
import os
from pathlib import Path
import subprocess  # nosec
import sys
import tempfile
import threading
import time
from typing import Any, ClassVar

try:
    from RestrictedPython import compile_restricted
    from RestrictedPython.Guards import safe_builtins

    RESTRICTED_PYTHON_AVAILABLE = True
except ImportError:
    RESTRICTED_PYTHON_AVAILABLE = False
    logging.warning("RestrictedPython not available. Python execution will be limited.")

from app.tool.base import BaseTool
from app.tool.base_tool import ToolCategory, ToolResult

logger = logging.getLogger(__name__)


class TimeoutError(Exception):
    """Custom timeout error for code execution."""

    pass


class CodeExecutionTool(BaseTool):
    """
    Tool for executing code in various programming languages with security measures.
    """

    name: str = "code_execution"
    description: str = "Execute code in various programming languages (Python, JavaScript, etc.)"
    category: ToolCategory = ToolCategory.DEVELOPMENT

    # Safety classification
    is_safe: bool = False
    requires_sandbox: bool = True

    class Config:
        arbitrary_types_allowed = True
        extra = "allow"

    # Execution limits
    DEFAULT_TIMEOUT: int = 30  # seconds
    MAX_OUTPUT_SIZE: int = 10000  # characters
    MAX_MEMORY_MB: int = 100  # MB (for subprocess)

    # Supported languages and their configurations
    SUPPORTED_LANGUAGES: ClassVar[dict[str, dict[str, Any]]] = {
        "python": {
            "extension": ".py",
            "command": [sys.executable],
            "restricted": True,
            "timeout": 30,
        },
        "javascript": {
            "extension": ".js",
            "command": ["node"],
            "restricted": False,
            "timeout": 15,
        },
        "typescript": {
            "extension": ".ts",
            "command": ["ts-node"],
            "restricted": False,
            "timeout": 15,
        },
        "bash": {
            "extension": ".sh",
            "command": ["bash"],
            "restricted": False,
            "timeout": 10,
        },
        "shell": {
            "extension": ".sh",
            "command": ["sh"],
            "restricted": False,
            "timeout": 10,
        },
    }

    # Dangerous Python imports/functions to block
    BLOCKED_IMPORTS: ClassVar[set] = {
        "os",
        "sys",
        "subprocess",
        "shutil",
        "tempfile",
        "pickle",
        "marshal",
        "importlib",
        "__import__",
        "eval",
        "exec",
        "compile",
        "open",
        "file",
        "input",
        "raw_input",
        "reload",
        "vars",
        "locals",
        "globals",
        "dir",
        "hasattr",
        "getattr",
        "setattr",
        "delattr",
        "callable",
    }

    def __init__(self):
        """Initialize the code execution tool."""
        super().__init__()
        self._setup_execution_environment()

    def _setup_execution_environment(self):
        """Set up the execution environment and verify dependencies."""
        self.temp_dir = tempfile.mkdtemp(prefix="code_exec_")
        logger.info(f"Code execution temporary directory: {self.temp_dir}")

        # Check available interpreters
        self.available_languages = []
        for lang, config in self.SUPPORTED_LANGUAGES.items():
            if lang == "python":
                self.available_languages.append(lang)
            else:
                # Check if interpreter is available
                try:
                    result = subprocess.run(  # nosec
                        config["command"] + ["--version"],
                        capture_output=True,
                        timeout=5,
                        text=True,
                        check=False,
                    )
                    if result.returncode == 0:
                        self.available_languages.append(lang)
                        logger.debug(f"{lang} interpreter available: {result.stdout.strip()}")
                except (
                    subprocess.TimeoutExpired,
                    FileNotFoundError,
                    subprocess.SubprocessError,
                ):
                    logger.warning(f"{lang} interpreter not available")

        logger.info(f"Available languages: {self.available_languages}")

    async def execute(self, code: str, language: str = "python", **kwargs) -> ToolResult:
        """
        Execute code in the specified language.

        Args:
            code: The code to execute
            language: Programming language (python, javascript, etc.)
            **kwargs: Additional parameters like timeout, memory_limit

        Returns:
            ToolResult with execution output and metadata

        """
        try:
            # Validate inputs
            if not code or not code.strip():
                return ToolResult(
                    success=False,
                    result="",
                    error="No code provided",
                    metadata={"language": language},
                )

            language = language.lower()
            if language not in self.available_languages:
                return ToolResult(
                    success=False,
                    result="",
                    error=f"Language '{language}' not supported. Available: {self.available_languages}",
                    metadata={
                        "language": language,
                        "available_languages": self.available_languages,
                    },
                )

            # Get execution parameters
            timeout = kwargs.get("timeout", self.DEFAULT_TIMEOUT)
            memory_limit = kwargs.get("memory_limit", self.MAX_MEMORY_MB)

            logger.info(f"Executing {language} code (timeout: {timeout}s)")

            # Execute based on language
            if language == "python":
                if RESTRICTED_PYTHON_AVAILABLE:
                    result = await self._execute_python_restricted(code, timeout)
                else:
                    result = await self._execute_python_subprocess(code, timeout, memory_limit)
            else:
                result = await self._execute_subprocess(code, language, timeout, memory_limit)

            return result

        except Exception as e:
            logger.error(f"Error executing {language} code: {e!s}")
            return ToolResult(
                success=False,
                result="",
                error=f"Execution error: {e!s}",
                metadata={"language": language},
            )

    async def _execute_python_restricted(self, code: str, timeout: int) -> ToolResult:
        """
        Execute Python code using RestrictedPython for security.

        Args:
            code: Python code to execute
            timeout: Execution timeout in seconds

        Returns:
            ToolResult with execution output

        """
        try:
            # Check for blocked imports
            for blocked in self.BLOCKED_IMPORTS:
                if blocked in code:
                    return ToolResult(
                        success=False,
                        result="",
                        error=f"Blocked import/function detected: {blocked}",
                        metadata={"language": "python", "security_violation": blocked},
                    )

            # Compile with restrictions
            compiled_code = compile_restricted(code, "<string>", "exec")
            if compiled_code is None:
                return ToolResult(
                    success=False,
                    result="",
                    error="Code compilation failed - contains restricted operations",
                    metadata={"language": "python"},
                )

            # Prepare restricted environment
            restricted_globals = {
                "__builtins__": {
                    **safe_builtins,
                    "print": print,
                    "len": len,
                    "str": str,
                    "int": int,
                    "float": float,
                    "bool": bool,
                    "list": list,
                    "dict": dict,
                    "tuple": tuple,
                    "set": set,
                    "range": range,
                    "enumerate": enumerate,
                    "zip": zip,
                    "map": map,
                    "filter": filter,
                    "sum": sum,
                    "min": max,
                    "max": max,
                    "abs": abs,
                    "round": round,
                    "sorted": sorted,
                    "reversed": reversed,
                }
            }

            # Capture output
            stdout_capture = StringIO()
            stderr_capture = StringIO()

            start_time = time.time()

            # Execute with timeout
            def execute_code():
                try:
                    with (
                        redirect_stdout(stdout_capture),
                        redirect_stderr(stderr_capture),
                    ):
                        exec(compiled_code, restricted_globals, {})  # nosec
                except Exception as e:
                    stderr_capture.write(f"Execution error: {e!s}")

            # Run in thread with timeout
            thread = threading.Thread(target=execute_code)
            thread.daemon = True
            thread.start()
            thread.join(timeout)

            execution_time = time.time() - start_time

            if thread.is_alive():
                return ToolResult(
                    success=False,
                    result="",
                    error=f"Code execution timed out after {timeout} seconds",
                    metadata={"language": "python", "timeout": timeout},
                )

            # Get output
            stdout_output = stdout_capture.getvalue()
            stderr_output = stderr_capture.getvalue()

            # Limit output size
            if len(stdout_output) > self.MAX_OUTPUT_SIZE:
                stdout_output = stdout_output[: self.MAX_OUTPUT_SIZE] + "\n... (output truncated)"

            success = len(stderr_output) == 0
            result_output = stdout_output if success else stderr_output

            return ToolResult(
                success=success,
                result=result_output,
                error=stderr_output if not success else None,
                metadata={
                    "language": "python",
                    "execution_time": execution_time,
                    "restricted": True,
                    "output_length": len(result_output),
                },
            )

        except Exception as e:
            logger.error(f"Error in restricted Python execution: {e!s}")
            return ToolResult(
                success=False,
                result="",
                error=f"Execution error: {e!s}",
                metadata={"language": "python", "restricted": True},
            )

    async def _execute_python_subprocess(self, code: str, timeout: int, memory_limit: int) -> ToolResult:
        """
        Execute Python code using subprocess as fallback.

        Args:
            code: Python code to execute
            timeout: Execution timeout in seconds
            memory_limit: Memory limit in MB

        Returns:
            ToolResult with execution output

        """
        return await self._execute_subprocess(code, "python", timeout, memory_limit)

    async def _execute_subprocess(
        self,
        code: str,
        language: str,
        timeout: int,
        memory_limit: int,  # noqa: ARG002
    ) -> ToolResult:
        """
        Execute code using subprocess with security measures.

        Args:
            code: Code to execute
            language: Programming language
            timeout: Execution timeout in seconds
            memory_limit: Memory limit in MB

        Returns:
            ToolResult with execution output

        """
        try:
            config = self.SUPPORTED_LANGUAGES[language]

            # Create temporary file
            temp_file = Path(self.temp_dir) / f"code_{int(time.time())}{config['extension']}"

            with temp_file.open("w", encoding="utf-8") as f:
                f.write(code)

            # Prepare command
            command = config["command"] + [temp_file]

            # Prepare environment with restrictions
            env = os.environ.copy()
            env["PYTHONDONTWRITEBYTECODE"] = "1"  # Don't create .pyc files

            start_time = time.time()

            # Execute with subprocess
            try:
                result = subprocess.run(  # nosec
                    command,
                    capture_output=True,
                    timeout=timeout,
                    text=True,
                    env=env,
                    cwd=self.temp_dir,
                    check=False,
                )

                execution_time = time.time() - start_time

                # Get output
                stdout_output = result.stdout
                stderr_output = result.stderr

                # Limit output size
                if len(stdout_output) > self.MAX_OUTPUT_SIZE:
                    stdout_output = stdout_output[: self.MAX_OUTPUT_SIZE] + "\n... (output truncated)"

                if len(stderr_output) > self.MAX_OUTPUT_SIZE:
                    stderr_output = stderr_output[: self.MAX_OUTPUT_SIZE] + "\n... (error output truncated)"

                success = result.returncode == 0
                result_output = stdout_output if success else stderr_output

                return ToolResult(
                    success=success,
                    result=result_output,
                    error=stderr_output if not success else None,
                    metadata={
                        "language": language,
                        "execution_time": execution_time,
                        "return_code": result.returncode,
                        "restricted": False,
                        "output_length": len(result_output),
                    },
                )

            except subprocess.TimeoutExpired:
                return ToolResult(
                    success=False,
                    result="",
                    error=f"Code execution timed out after {timeout} seconds",
                    metadata={"language": language, "timeout": timeout},
                )

            finally:
                # Clean up temporary file
                with suppress(OSError):
                    Path(temp_file).unlink()

        except Exception as e:
            logger.error(f"Error in subprocess execution: {e!s}")
            return ToolResult(
                success=False,
                result="",
                error=f"Execution error: {e!s}",
                metadata={"language": language},
            )

    def get_schema(self) -> dict[str, Any]:
        """Get the JSON schema for this tool."""
        return {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "The code to execute"},
                "language": {
                    "type": "string",
                    "enum": list(self.SUPPORTED_LANGUAGES.keys()),
                    "default": "python",
                    "description": "Programming language for the code",
                },
                "timeout": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 60,
                    "default": self.DEFAULT_TIMEOUT,
                    "description": "Execution timeout in seconds",
                },
                "memory_limit": {
                    "type": "integer",
                    "minimum": 10,
                    "maximum": 500,
                    "default": self.MAX_MEMORY_MB,
                    "description": "Memory limit in MB",
                },
            },
            "required": ["code"],
            "additionalProperties": False,
        }

    def get_examples(self) -> list[dict[str, Any]]:
        """Get usage examples for this tool."""
        return [
            {
                "name": "Python calculation",
                "description": "Execute Python code for mathematical calculations",
                "parameters": {
                    "code": "result = 2 + 2\nprint(f'2 + 2 = {result}')",
                    "language": "python",
                },
            },
            {
                "name": "JavaScript array operations",
                "description": "Execute JavaScript code for array manipulation",
                "parameters": {
                    "code": "const numbers = [1, 2, 3, 4, 5];\nconst sum = numbers.reduce((a, b) => a + b, 0);\nconsole.log(`Sum: ${sum}`);",
                    "language": "javascript",
                },
            },
            {
                "name": "Data analysis",
                "description": "Python code for simple data analysis",
                "parameters": {
                    "code": "data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]\naverage = sum(data) / len(data)\nprint(f'Data: {data}')\nprint(f'Average: {average}')\nprint(f'Max: {max(data)}')\nprint(f'Min: {min(data)}')",
                    "language": "python",
                },
            },
        ]

    def cleanup(self):
        """Clean up temporary resources."""
        try:
            import shutil

            if hasattr(self, "temp_dir") and Path(self.temp_dir).exists():
                shutil.rmtree(self.temp_dir)
                logger.info(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            logger.error(f"Error cleaning up temporary directory: {e!s}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()


# Register the tool
def register_code_execution_tool():
    """Register the code execution tool."""
    from app.tool.registry import tool_registry

    tool = CodeExecutionTool()
    tool_registry.register_tool("code_execution", tool)
    logger.info("Code execution tool registered successfully")

    return tool


# Auto-register when module is imported
if __name__ != "__main__":
    register_code_execution_tool()
