"""
Servidor MCP especializado em desenvolvimento de software
"""

import asyncio
import os
from pathlib import Path
from typing import Any

from mcp import types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from mcp.types import InitializeResult, Resource, Tool

# Configuração centralizada via settings
from app.core.settings import settings

SPECIALIZATION = os.getenv("SPECIALIZATION", "development")  # Mantido por ser específico do MCP
# Tentar obter tools das configurações MCP, senão usar valor padrão
default_tools = "filesystem,code_execution,git,testing"
mcp_server_config = settings.mcp_config.servers.get("development", {})
tools_str = os.getenv("TOOLS", mcp_server_config.get("tools", default_tools))
TOOLS = tools_str.split(",")

# Criar servidor MCP
server = Server("openmanus-development-agent")


@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """Lista recursos disponíveis para desenvolvimento"""
    return [
        Resource(
            uri="development://capabilities",
            name="Development Capabilities",
            description="Capacidades especializadas de desenvolvimento",
            mimeType="application/json",
        ),
        Resource(
            uri="development://tools",
            name="Development Tools",
            description="Ferramentas de desenvolvimento disponíveis",
            mimeType="application/json",
        ),
    ]


@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Lê conteúdo de recursos de desenvolvimento"""
    if uri == "development://capabilities":
        return """
        {
            "specialization": "development",
            "expertise": [
                "python", "javascript", "web_development",
                "api_development", "testing", "debugging"
            ],
            "primary_tools": ["filesystem", "code_execution", "git"],
            "secondary_tools": ["testing", "debugging"],
            "capabilities": [
                "Code generation and modification",
                "File system operations",
                "Git version control",
                "Test execution and debugging",
                "API development and testing",
                "Web application development"
            ]
        }
        """
    if uri == "development://tools":
        return f"""
        {{
            "available_tools": {TOOLS},
            "status": "active",
            "last_updated": "{asyncio.get_event_loop().time()}"
        }}
        """
    raise ValueError(f"Unknown resource: {uri}")


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """Lista ferramentas de desenvolvimento disponíveis"""
    tools = []

    if "filesystem" in TOOLS:
        tools.append(
            Tool(
                name="dev_file_operations",
                description="Operações avançadas de sistema de arquivos para desenvolvimento",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": [
                                "read",
                                "write",
                                "create",
                                "delete",
                                "list",
                                "search",
                                "backup",
                            ],
                        },
                        "path": {"type": "string"},
                        "content": {"type": "string", "optional": True},
                        "pattern": {"type": "string", "optional": True},
                        "backup_name": {"type": "string", "optional": True},
                    },
                    "required": ["operation", "path"],
                },
            )
        )

    if "code_execution" in TOOLS:
        tools.append(
            Tool(
                name="dev_code_execution",
                description="Execução segura de código com monitoramento",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "language": {
                            "type": "string",
                            "enum": ["python", "javascript", "bash", "sql"],
                        },
                        "code": {"type": "string"},
                        "timeout": {"type": "number", "default": 30},
                        "safe_mode": {"type": "boolean", "default": True},
                    },
                    "required": ["language", "code"],
                },
            )
        )

    if "git" in TOOLS:
        tools.append(
            Tool(
                name="dev_git_operations",
                description="Operações Git avançadas para desenvolvimento",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "operation": {
                            "type": "string",
                            "enum": [
                                "status",
                                "add",
                                "commit",
                                "push",
                                "pull",
                                "branch",
                                "merge",
                                "diff",
                            ],
                        },
                        "repository": {"type": "string"},
                        "message": {"type": "string", "optional": True},
                        "branch": {"type": "string", "optional": True},
                        "files": {
                            "type": "array",
                            "items": {"type": "string"},
                            "optional": True,
                        },
                    },
                    "required": ["operation", "repository"],
                },
            )
        )

    if "testing" in TOOLS:
        tools.append(
            Tool(
                name="dev_testing",
                description="Execução e análise de testes de software",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "test_type": {
                            "type": "string",
                            "enum": [
                                "unit",
                                "integration",
                                "functional",
                                "performance",
                            ],
                        },
                        "test_path": {"type": "string"},
                        "framework": {
                            "type": "string",
                            "enum": ["pytest", "unittest", "jest", "mocha"],
                            "optional": True,
                        },
                        "coverage": {"type": "boolean", "default": False},
                    },
                    "required": ["test_type", "test_path"],
                },
            )
        )

    return tools


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any]
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Executa ferramentas de desenvolvimento"""
    if name == "dev_file_operations":
        operation = arguments.get("operation")
        path = arguments.get("path")

        # Implementação básica de operações de arquivo
        try:
            if operation == "read":
                with Path(path).open(encoding="utf-8") as f:
                    content = f.read()
                return [types.TextContent(type="text", text=f"File content:\n{content}")]

            if operation == "write":
                content = arguments.get("content", "")
                with Path(path).open("w", encoding="utf-8") as f:
                    f.write(content)
                return [types.TextContent(type="text", text=f"Successfully wrote to {path}")]

            if operation == "list":
                files = [f.name for f in Path(path).iterdir()]
                return [types.TextContent(type="text", text=f"Files in {path}:\n" + "\n".join(files))]

            return [types.TextContent(type="text", text=f"Operation {operation} not yet implemented")]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error in file operation: {e!s}")]

    elif name == "dev_code_execution":
        language = arguments.get("language")
        code = arguments.get("code")
        timeout = arguments.get("timeout", 30)

        # Implementação básica de execução de código
        try:
            if language == "python":
                import subprocess  # nosec

                result = subprocess.run(  # nosec
                    ["python", "-c", code],
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False,
                )
                output = result.stdout if result.returncode == 0 else result.stderr
                return [types.TextContent(type="text", text=f"Execution result:\n{output}")]

            return [types.TextContent(type="text", text=f"Language {language} not yet supported")]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error executing code: {e!s}")]

    elif name == "dev_git_operations":
        operation = arguments.get("operation")
        repository = arguments.get("repository")

        # Implementação básica de operações Git
        try:
            import os
            import subprocess  # nosec

            os.chdir(repository)

            if operation == "status":
                result = subprocess.run(["git", "status"], capture_output=True, text=True, check=False)  # nosec
            elif operation == "add":
                files = arguments.get("files", ["."])
                result = subprocess.run(["git", "add", *files], capture_output=True, text=True, check=False)  # nosec
            elif operation == "commit":
                message = arguments.get("message", "Automated commit")
                result = subprocess.run(  # nosec
                    ["git", "commit", "-m", message],
                    capture_output=True,
                    text=True,
                    check=False,
                )  # nosec
            else:
                result = subprocess.run(["git", operation], capture_output=True, text=True, check=False)  # nosec

            output = result.stdout if result.returncode == 0 else result.stderr
            return [types.TextContent(type="text", text=f"Git {operation} result:\n{output}")]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error in git operation: {e!s}")]

    elif name == "dev_testing":
        arguments.get("test_type")
        test_path = arguments.get("test_path")
        framework = arguments.get("framework", "pytest")

        # Implementação básica de execução de testes
        try:
            import subprocess  # nosec

            if framework == "pytest":
                cmd = ["python", "-m", "pytest", test_path, "-v"]
                if arguments.get("coverage"):
                    cmd.extend(["--cov=.", "--cov-report=term-missing"])
            else:
                cmd = ["python", "-m", "unittest", test_path]

            result = subprocess.run(cmd, capture_output=True, text=True, check=False)  # nosec
            output = result.stdout + result.stderr

            return [types.TextContent(type="text", text=f"Test execution result:\n{output}")]

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error running tests: {e!s}")]

    else:
        return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    # Inicializar e executar servidor via stdio
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializeResult(
                protocolVersion="2024-11-05",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
