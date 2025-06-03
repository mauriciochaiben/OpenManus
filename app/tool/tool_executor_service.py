"""
Tool Executor Service

Enhanced service for executing tools with sandboxing support for unsafe tools.
Uses Docker containers for isolated execution of potentially dangerous code.
"""

import asyncio
import json
import logging
import shutil
import tempfile
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

try:
    import docker
    from docker.errors import APIError, DockerException

    DOCKER_AVAILABLE = True
except ImportError:
    DOCKER_AVAILABLE = False
    logging.warning(
        "Docker SDK not available. Unsafe tools will use restricted execution."
    )

from app.core.exceptions import SecurityError, ValidationError
from app.core.settings import settings
from app.tool.base_tool import BaseTool, ToolCategory, ToolResult
from app.tool.tool_registry import ToolRegistry

logger = logging.getLogger(__name__)


class ExecutionMode(Enum):
    """Execution modes for tools."""

    DIRECT = "direct"  # Direct execution in current process
    RESTRICTED = "restricted"  # Restricted execution with limitations
    SANDBOXED = "sandboxed"  # Docker container execution


@dataclass
class SandboxConfig:
    """Configuration for sandbox execution."""

    image: str = "python:3.11-alpine"
    timeout: int = 30
    memory_limit: str = "128m"
    cpu_limit: float = 0.5
    network_disabled: bool = True
    read_only: bool = True
    temp_dir_size: str = "10m"
    max_output_size: int = 10000


@dataclass
class ExecutionContext:
    """Context for tool execution."""

    tool: BaseTool
    parameters: dict[str, Any]
    mode: ExecutionMode
    sandbox_config: SandboxConfig | None = None
    execution_id: str = ""
    start_time: float = 0
    container_id: str | None = None


class ToolExecutorService:
    """
    Enhanced service for executing tools with sandboxing capabilities.

    Provides secure execution of tools using Docker containers for unsafe operations,
    with configurable resource limits and cleanup mechanisms.
    """

    # Tool safety classification
    UNSAFE_TOOLS = {
        "code_execution",
        "file_manager",
        "system_command",
        "shell_executor",
    }

    # Default sandbox configurations by tool category
    DEFAULT_SANDBOX_CONFIGS = {
        ToolCategory.DEVELOPMENT: SandboxConfig(
            image="python:3.11-alpine", timeout=60, memory_limit="256m", cpu_limit=1.0
        ),
        ToolCategory.SYSTEM: SandboxConfig(
            image="ubuntu:22.04", timeout=30, memory_limit="128m", cpu_limit=0.5
        ),
        ToolCategory.ANALYSIS: SandboxConfig(
            image="python:3.11-slim", timeout=120, memory_limit="512m", cpu_limit=1.5
        ),
    }

    def __init__(self):
        """Initialize the tool executor service."""
        self.docker_client = None
        self.active_containers: dict[str, str] = {}  # execution_id -> container_id
        self._setup_docker()

    def _setup_docker(self):
        """Set up Docker client if available."""
        if not DOCKER_AVAILABLE:
            logger.warning(
                "Docker not available. Unsafe tools will use restricted execution."
            )
            return

        try:
            self.docker_client = docker.from_env()
            # Test Docker connection
            self.docker_client.ping()
            logger.info("Docker client initialized successfully")

            # Pull required images
            self._ensure_sandbox_images()

        except DockerException as e:
            logger.error(f"Failed to initialize Docker client: {str(e)}")
            self.docker_client = None

    def _ensure_sandbox_images(self):
        """Ensure required Docker images are available."""
        required_images = set()
        for config in self.DEFAULT_SANDBOX_CONFIGS.values():
            required_images.add(config.image)

        for image in required_images:
            try:
                self.docker_client.images.get(image)
                logger.debug(f"Docker image {image} available")
            except docker.errors.ImageNotFound:
                logger.info(f"Pulling Docker image: {image}")
                try:
                    self.docker_client.images.pull(image)
                    logger.info(f"Successfully pulled image: {image}")
                except APIError as e:
                    logger.error(f"Failed to pull image {image}: {str(e)}")

    async def execute_tool(
        self,
        tool_name: str,
        parameters: dict[str, Any],
        force_sandbox: bool = False,
        sandbox_config: SandboxConfig | None = None,
    ) -> ToolResult:
        """
        Execute a tool with appropriate security measures.

        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
            force_sandbox: Force sandbox execution even for safe tools
            sandbox_config: Custom sandbox configuration

        Returns:
            ToolResult with execution output and metadata
        """
        execution_id = f"exec_{int(time.time())}_{id(self)}"

        try:
            # Get tool from registry
            tool = ToolRegistry.get_tool(tool_name)
            if not tool:
                return ToolResult(
                    success=False,
                    result="",
                    error=f"Tool '{tool_name}' not found",
                    metadata={"tool_name": tool_name},
                )

            # Determine execution mode
            mode = self._determine_execution_mode(tool, force_sandbox)

            # Create execution context
            context = ExecutionContext(
                tool=tool,
                parameters=parameters,
                mode=mode,
                sandbox_config=sandbox_config,
                execution_id=execution_id,
                start_time=time.time(),
            )

            logger.info(f"Executing tool '{tool_name}' in {mode.value} mode")

            # Execute based on mode
            if mode == ExecutionMode.SANDBOXED:
                result = await self._execute_sandboxed(context)
            elif mode == ExecutionMode.RESTRICTED:
                result = await self._execute_restricted(context)
            else:
                result = await self._execute_direct(context)

            # Add execution metadata
            execution_time = time.time() - context.start_time
            result.metadata.update(
                {
                    "execution_id": execution_id,
                    "execution_mode": mode.value,
                    "execution_time": execution_time,
                    "tool_name": tool_name,
                }
            )

            return result

        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {str(e)}")
            return ToolResult(
                success=False,
                result="",
                error=f"Tool execution failed: {str(e)}",
                metadata={
                    "tool_name": tool_name,
                    "execution_id": execution_id,
                    "execution_mode": "error",
                },
            )

        finally:
            # Cleanup if needed
            await self._cleanup_execution(execution_id)

    def _determine_execution_mode(
        self, tool: BaseTool, force_sandbox: bool
    ) -> ExecutionMode:
        """
        Determine the appropriate execution mode for a tool.

        Args:
            tool: Tool to execute
            force_sandbox: Whether to force sandbox execution

        Returns:
            Appropriate execution mode
        """
        if force_sandbox:
            return (
                ExecutionMode.SANDBOXED
                if self.docker_client
                else ExecutionMode.RESTRICTED
            )

        if tool.name in self.UNSAFE_TOOLS:
            if self.docker_client:
                return ExecutionMode.SANDBOXED
            logger.warning(
                f"Tool '{tool.name}' is unsafe but Docker unavailable. Using restricted mode."
            )
            return ExecutionMode.RESTRICTED

        return ExecutionMode.DIRECT

    async def _execute_direct(self, context: ExecutionContext) -> ToolResult:
        """Execute tool directly in current process."""
        try:
            return await context.tool.execute(**context.parameters)
        except Exception as e:
            logger.error(f"Direct execution failed: {str(e)}")
            raise

    async def _execute_restricted(self, context: ExecutionContext) -> ToolResult:
        """Execute tool with restrictions but no sandboxing."""
        try:
            # Add timeout and resource monitoring
            timeout = getattr(settings, "tool_execution_timeout", 30)

            # Execute with timeout
            return await asyncio.wait_for(
                context.tool.execute(**context.parameters), timeout=timeout
            )

        except TimeoutError:
            return ToolResult(
                success=False,
                result="",
                error=f"Tool execution timed out after {timeout} seconds",
                metadata={"timeout": timeout},
            )
        except Exception as e:
            logger.error(f"Restricted execution failed: {str(e)}")
            raise

    async def _execute_sandboxed(self, context: ExecutionContext) -> ToolResult:
        """Execute tool in Docker sandbox."""
        if not self.docker_client:
            logger.warning("Docker not available, falling back to restricted execution")
            return await self._execute_restricted(context)

        try:
            # Get or create sandbox config
            sandbox_config = context.sandbox_config or self._get_default_sandbox_config(
                context.tool
            )

            # Prepare sandbox environment
            container_setup = await self._prepare_sandbox(context, sandbox_config)
            context.container_id = container_setup["container_id"]

            # Execute in container
            return await self._execute_in_container(
                context, container_setup, sandbox_config
            )

        except Exception as e:
            logger.error(f"Sandbox execution failed: {str(e)}")
            raise SecurityError(f"Sandbox execution failed: {str(e)}") from e

    def _get_default_sandbox_config(self, tool: BaseTool) -> SandboxConfig:
        """Get default sandbox configuration for a tool."""
        return self.DEFAULT_SANDBOX_CONFIGS.get(
            tool.category,
            SandboxConfig(),  # Use default config
        )

    async def _prepare_sandbox(
        self, context: ExecutionContext, config: SandboxConfig
    ) -> dict[str, Any]:
        """
        Prepare Docker sandbox environment.

        Args:
            context: Execution context
            config: Sandbox configuration

        Returns:
            Container setup information
        """
        try:
            # Create temporary directory for code/files
            temp_dir = tempfile.mkdtemp(prefix=f"sandbox_{context.execution_id}_")

            # Prepare execution script based on tool type
            script_path = await self._prepare_execution_script(context, temp_dir)

            # Container configuration
            container_config = {
                "image": config.image,
                "command": self._get_container_command(context.tool, script_path),
                "volumes": {temp_dir: {"bind": "/workspace", "mode": "rw"}},
                "working_dir": "/workspace",
                "mem_limit": config.memory_limit,
                "cpu_quota": int(config.cpu_limit * 100000),
                "cpu_period": 100000,
                "network_disabled": config.network_disabled,
                "read_only": config.read_only,
                "tmpfs": {"/tmp": f"size={config.temp_dir_size}"},
                "detach": True,
                "stdout": True,
                "stderr": True,
                "remove": True,  # Auto-remove when finished
                "user": "nobody",  # Run as non-root user
                "cap_drop": ["ALL"],  # Drop all capabilities
                "security_opt": ["no-new-privileges"],
            }

            # Create container
            container = self.docker_client.containers.create(**container_config)

            # Track container
            self.active_containers[context.execution_id] = container.id

            return {
                "container_id": container.id,
                "container": container,
                "temp_dir": temp_dir,
                "script_path": script_path,
            }

        except Exception as e:
            logger.error(f"Failed to prepare sandbox: {str(e)}")
            raise SecurityError(f"Sandbox preparation failed: {str(e)}") from e

    async def _prepare_execution_script(
        self, context: ExecutionContext, temp_dir: str
    ) -> str:
        """
        Prepare execution script for the tool.

        Args:
            context: Execution context
            temp_dir: Temporary directory path

        Returns:
            Path to the execution script
        """
        tool_name = context.tool.name
        parameters = context.parameters

        if tool_name == "code_execution":
            # Special handling for code execution
            return await self._prepare_code_execution_script(parameters, temp_dir)
        # Generic tool execution script
        return await self._prepare_generic_tool_script(context, temp_dir)

    async def _prepare_code_execution_script(
        self, parameters: dict[str, Any], temp_dir: str
    ) -> str:
        """Prepare script for code execution tool."""
        code = parameters.get("code", "")
        language = parameters.get("language", "python")

        if language == "python":
            # Create Python script
            script_path = Path(temp_dir) / "execute.py"
            with script_path.open("w", encoding="utf-8") as f:
                f.write(code)
            return "/workspace/execute.py"

        if language == "javascript":
            # Create JavaScript file
            script_path = Path(temp_dir) / "execute.js"
            with script_path.open("w", encoding="utf-8") as f:
                f.write(code)
            return "/workspace/execute.js"

        raise ValidationError(f"Unsupported language for sandbox: {language}")

    async def _prepare_generic_tool_script(
        self, context: ExecutionContext, temp_dir: str
    ) -> str:
        """Prepare generic tool execution script."""
        # Create a Python wrapper script that imports and executes the tool
        script_content = f"""
import sys
import json
import asyncio
from pathlib import Path

# Add tool path
sys.path.append('/app')

async def main():
    try:
        # Import tool (this would need the actual tool available in container)
        from app.tool.{context.tool.name} import {context.tool.__class__.__name__}

        # Execute tool
        tool = {context.tool.__class__.__name__}()
        parameters = {json.dumps(context.parameters)}

        result = await tool.execute(**parameters)

        # Output result as JSON
        print(json.dumps({{
            "success": result.success,
            "result": result.result,
            "error": result.error,
            "metadata": result.metadata
        }}))

    except Exception as e:
        print(json.dumps({{
            "success": False,
            "result": "",
            "error": str(e),
            "metadata": {{}}
        }}))

if __name__ == "__main__":
    asyncio.run(main())
"""

        script_path = Path(temp_dir) / "tool_wrapper.py"
        with script_path.open("w", encoding="utf-8") as f:
            f.write(script_content)

        return "/workspace/tool_wrapper.py"

    def _get_container_command(self, tool: BaseTool, script_path: str) -> list[str]:
        """Get container execution command."""
        if tool.name == "code_execution":
            if script_path.endswith(".py"):
                return ["python", script_path]
            if script_path.endswith(".js"):
                return ["node", script_path]

        return ["python", script_path]

    async def _execute_in_container(
        self,
        context: ExecutionContext,
        container_setup: dict[str, Any],
        config: SandboxConfig,
    ) -> ToolResult:
        """
        Execute tool in the prepared container.

        Args:
            context: Execution context
            container_setup: Container setup information
            config: Sandbox configuration

        Returns:
            Tool execution result
        """
        container = container_setup["container"]
        temp_dir = container_setup["temp_dir"]

        try:
            # Start container
            container.start()

            # Wait for completion with timeout
            try:
                exit_code = container.wait(timeout=config.timeout)

                # Get output
                logs = container.logs(stdout=True, stderr=True).decode("utf-8")

                # Parse output
                if exit_code["StatusCode"] == 0:
                    # Successful execution
                    if context.tool.name == "code_execution":
                        # For code execution, the output is the result
                        result = logs.strip()
                        return ToolResult(
                            success=True,
                            result=result,
                            error=None,
                            metadata={
                                "container_id": container.id,
                                "exit_code": exit_code["StatusCode"],
                            },
                        )
                    # For other tools, try to parse JSON output
                    try:
                        result_data = json.loads(logs.strip())
                        return ToolResult(**result_data)
                    except json.JSONDecodeError:
                        return ToolResult(
                            success=True,
                            result=logs.strip(),
                            error=None,
                            metadata={"container_id": container.id},
                        )
                else:
                    # Execution failed
                    return ToolResult(
                        success=False,
                        result="",
                        error=logs.strip(),
                        metadata={
                            "container_id": container.id,
                            "exit_code": exit_code["StatusCode"],
                        },
                    )

            except Exception as e:
                # Timeout or other error
                container.kill()
                return ToolResult(
                    success=False,
                    result="",
                    error=f"Container execution failed: {str(e)}",
                    metadata={"container_id": container.id},
                )

        finally:
            # Cleanup
            try:
                if container.status != "exited":
                    container.kill()
                container.remove(force=True)
            except Exception as e:
                logger.warning(f"Failed to cleanup container {container.id}: {str(e)}")

            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp dir {temp_dir}: {str(e)}")

    async def _cleanup_execution(self, execution_id: str):
        """Clean up resources for an execution."""
        if execution_id in self.active_containers:
            container_id = self.active_containers.pop(execution_id)
            try:
                container = self.docker_client.containers.get(container_id)
                if container.status != "exited":
                    container.kill()
                container.remove(force=True)
                logger.debug(f"Cleaned up container {container_id}")
            except Exception as e:
                logger.warning(f"Failed to cleanup container {container_id}: {str(e)}")

    async def list_active_executions(self) -> list[dict[str, Any]]:
        """List currently active executions."""
        active = []
        for execution_id, container_id in self.active_containers.items():
            try:
                container = self.docker_client.containers.get(container_id)
                active.append(
                    {
                        "execution_id": execution_id,
                        "container_id": container_id,
                        "status": container.status,
                        "created": container.attrs.get("Created", "unknown"),
                    }
                )
            except Exception:
                # Container might have been removed
                pass

        return active

    async def kill_execution(self, execution_id: str) -> bool:
        """Kill a running execution."""
        if execution_id not in self.active_containers:
            return False

        try:
            await self._cleanup_execution(execution_id)
            return True
        except Exception as e:
            logger.error(f"Failed to kill execution {execution_id}: {str(e)}")
            return False

    def __del__(self):
        """Cleanup on destruction."""
        try:
            # Kill all active containers
            for execution_id in list(self.active_containers.keys()):
                asyncio.create_task(self._cleanup_execution(execution_id))
        except Exception:
            pass


# Global instance
_tool_executor = None


def get_tool_executor() -> ToolExecutorService:
    """Get global tool executor instance."""
    global _tool_executor
    if _tool_executor is None:
        _tool_executor = ToolExecutorService()
    return _tool_executor
