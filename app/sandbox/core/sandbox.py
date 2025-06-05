import asyncio
import io
import os
import tarfile
import tempfile
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

try:
    import docker
    from docker.errors import NotFound
except Exception:  # pragma: no cover - optional dependency missing
    docker = None
    class NotFound(Exception):
        pass

from app.core.settings import SandboxSettings
from app.sandbox.core.exceptions import SandboxTimeoutError
from app.sandbox.core.terminal import AsyncDockerizedTerminal

if TYPE_CHECKING:
    from docker.models.containers import Container


class DockerSandbox:
    """Docker sandbox environment.

    Provides a containerized execution environment with resource limits,
    file operations, and command execution capabilities.

    Attributes:
        config: Sandbox configuration.
        volume_bindings: Volume mapping configuration.
        client: Docker client.
        container: Docker container instance.
        terminal: Container terminal interface.
    """

    def __init__(
        self,
        config: SandboxSettings | None = None,
        volume_bindings: dict[str, str] | None = None,
    ):
        """Initializes a sandbox instance.

        Args:
            config: Sandbox configuration. Default configuration used if None.
            volume_bindings: Volume mappings in {host_path: container_path} format.
        """
        self.config = config or SandboxSettings()
        self.volume_bindings = volume_bindings or {}
        self.client = docker.from_env()
        self.container: Container | None = None
        self.terminal: AsyncDockerizedTerminal | None = None

    async def create(self) -> "DockerSandbox":
        """Creates and starts the sandbox container.

        Returns:
            Current sandbox instance.

        Raises:
            docker.errors.APIError: If Docker API call fails.
            RuntimeError: If container creation or startup fails.
        """
        try:
            # Prepare container config
            host_config = self.client.api.create_host_config(
                mem_limit=self.config.memory_limit,
                cpu_period=100000,
                cpu_quota=int(100000 * self.config.cpu_limit),
                network_mode="none" if not self.config.network_enabled else "bridge",
                binds=self._prepare_volume_bindings(),
            )

            # Generate unique container name with sandbox_ prefix
            container_name = f"sandbox_{uuid.uuid4().hex[:8]}"

            # Create container
            container = await asyncio.to_thread(
                self.client.api.create_container,
                image=self.config.image,
                command="tail -f /dev/null",
                hostname="sandbox",
                working_dir=self.config.work_dir,
                host_config=host_config,
                name=container_name,
                tty=True,
                detach=True,
            )

            self.container = self.client.containers.get(container["Id"])

            # Start container
            await asyncio.to_thread(self.container.start)

            # Initialize terminal
            self.terminal = AsyncDockerizedTerminal(
                container["Id"],
                self.config.work_dir,
                env_vars={"PYTHONUNBUFFERED": "1"},
                # Ensure Python output is not buffered
            )
            await self.terminal.init()

            return self

        except Exception as e:
            await self.cleanup()  # Ensure resources are cleaned up
            raise RuntimeError(f"Failed to create sandbox: {e}") from e

    def _prepare_volume_bindings(self) -> dict[str, dict[str, str]]:
        """Prepares volume binding configuration.

        Returns:
            Volume binding configuration dictionary.
        """
        bindings = {}

        # Create and add working directory mapping
        work_dir = self._ensure_host_dir(self.config.work_dir)
        bindings[work_dir] = {"bind": self.config.work_dir, "mode": "rw"}

        # Add custom volume bindings
        for host_path, container_path in self.volume_bindings.items():
            bindings[host_path] = {"bind": container_path, "mode": "rw"}

        return bindings

    @staticmethod
    def _ensure_host_dir(path: str) -> str:
        """Ensures directory exists on the host.

        Args:
            path: Directory path.

        Returns:
            Actual path on the host.
        """
        host_path = Path(tempfile.gettempdir()) / f"sandbox_{Path(path).name}_{os.urandom(4).hex()}"
        host_path.mkdir(parents=True, exist_ok=True)
        return str(host_path)

    async def run_command(self, cmd: str, timeout: int | None = None) -> str:
        """Runs a command in the sandbox.

        Args:
            cmd: Command to execute.
            timeout: Timeout in seconds.

        Returns:
            Command output as string.

        Raises:
            RuntimeError: If sandbox not initialized or command execution fails.
            TimeoutError: If command execution times out.
        """
        if not self.terminal:
            raise RuntimeError("Sandbox not initialized")

        try:
            return await self.terminal.run_command(cmd, timeout=timeout or self.config.timeout)
        except TimeoutError as e:
            raise SandboxTimeoutError(
                f"Command execution timed out after {timeout or self.config.timeout} seconds"
            ) from e

    async def read_file(self, path: str) -> str:
        """Reads a file from the container.

        Args:
            path: File path.

        Returns:
            File contents as string.

        Raises:
            FileNotFoundError: If file does not exist.
            RuntimeError: If read operation fails.
        """
        if not self.container:
            raise RuntimeError("Sandbox not initialized")

        try:
            # Get file archive
            resolved_path = self._safe_resolve_path(path)
            tar_stream, _ = await asyncio.to_thread(self.container.get_archive, resolved_path)

            # Read file content from tar stream
            content = await self._read_from_tar(tar_stream)
            return content.decode("utf-8")

        except NotFound as e:
            raise FileNotFoundError(f"File not found: {path}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to read file: {e}") from e

    async def write_file(self, path: str, content: str) -> None:
        """Writes content to a file in the container.

        Args:
            path: Target path.
            content: File content.

        Raises:
            RuntimeError: If write operation fails.
        """
        if not self.container:
            raise RuntimeError("Sandbox not initialized")

        try:
            resolved_path = self._safe_resolve_path(path)
            parent_dir = Path(resolved_path).parent

            # Create parent directory
            if parent_dir != Path(resolved_path).root:
                await self.run_command(f"mkdir -p {parent_dir}")

            # Prepare file data
            tar_stream = await self._create_tar_stream(Path(path).name, content.encode("utf-8"))

            # Write file
            await asyncio.to_thread(self.container.put_archive, parent_dir or "/", tar_stream)

        except Exception as e:
            raise RuntimeError(f"Failed to write file: {e}") from e

    def _safe_resolve_path(self, path: str) -> str:
        """Safely resolves container path, preventing path traversal.

        Args:
            path: Original path.

        Returns:
            Resolved absolute path.

        Raises:
            ValueError: If path contains potentially unsafe patterns.
        """
        # Check for path traversal attempts
        if ".." in path.split("/"):
            raise ValueError("Path contains potentially unsafe patterns")

        return str(Path(self.config.work_dir) / path) if not Path(path).is_absolute() else path

    async def copy_from(self, src_path: str, dst_path: str) -> None:
        """Copies a file from the container.

        Args:
            src_path: Source file path (container).
            dst_path: Destination path (host).

        Raises:
            FileNotFoundError: If source file does not exist.
            RuntimeError: If copy operation fails.
        """
        try:
            # Ensure destination file's parent directory exists
            parent_dir = Path(dst_path).parent
            if parent_dir != Path(dst_path).root:
                parent_dir.mkdir(parents=True, exist_ok=True)

            # Get file stream
            resolved_src = self._safe_resolve_path(src_path)
            stream, stat = await asyncio.to_thread(self.container.get_archive, resolved_src)

            # Create temporary directory to extract file
            with tempfile.TemporaryDirectory() as tmp_dir:
                # Write stream to temporary file
                tar_path = Path(tmp_dir) / "temp.tar"
                with tar_path.open("wb") as f:
                    for chunk in stream:
                        f.write(chunk)

                # Extract file safely
                with tarfile.open(tar_path) as tar:
                    members = tar.getmembers()
                    if not members:
                        raise FileNotFoundError(f"Source file is empty: {src_path}")

                    # If destination is a directory, we should preserve relative path structure
                    if Path(dst_path).is_dir():
                        # Safe extraction to prevent path traversal attacks
                        def is_safe_path(path, base_path):
                            """Check if extraction path is safe"""
                            return (
                                Path(base_path).resolve() in Path(path).resolve().parents
                                or Path(path).resolve() == Path(base_path).resolve()
                            )

                        safe_members = []
                        for member in members:
                            if member.isreg() or member.isdir():
                                target_path = Path(dst_path) / member.name
                                if is_safe_path(target_path, dst_path):
                                    safe_members.append(member)
                        tar.extractall(dst_path, members=safe_members)
                    else:
                        # If destination is a file, we only extract the source file's content
                        if len(members) > 1:
                            raise RuntimeError(f"Source path is a directory but destination is a file: {src_path}")

                        with Path(dst_path).open("wb") as dst:
                            src_file = tar.extractfile(members[0])
                            if src_file is None:
                                raise RuntimeError(f"Failed to extract file: {src_path}")
                            dst.write(src_file.read())

        except docker.errors.NotFound as e:
            raise FileNotFoundError(f"Source file not found: {src_path}") from e
        except Exception as e:
            raise RuntimeError(f"Failed to copy file: {e}") from e

    async def copy_to(self, src_path: str, dst_path: str) -> None:
        """Copies a file to the container.

        Args:
            src_path: Source file path (host).
            dst_path: Destination path (container).

        Raises:
            FileNotFoundError: If source file does not exist.
            RuntimeError: If copy operation fails.
        """
        try:
            if not Path(src_path).exists():
                raise FileNotFoundError(f"Source file not found: {src_path}")

            # Create destination directory in container
            resolved_dst = self._safe_resolve_path(dst_path)
            container_dir = Path(resolved_dst).parent
            if container_dir != Path(resolved_dst).root:
                await self.run_command(f"mkdir -p {container_dir}")

            # Create tar file to upload
            with tempfile.TemporaryDirectory() as tmp_dir:
                tar_path = Path(tmp_dir) / "temp.tar"
                with tarfile.open(tar_path, "w") as tar:
                    # Handle directory source path
                    if Path(src_path).is_dir():
                        # Get the directory name for archiving
                        for root, _, files in os.walk(src_path):
                            for file in files:
                                file_path = Path(root) / file
                                arcname = Path(dst_path).name / Path(file_path).relative_to(src_path)
                                tar.add(file_path, arcname=arcname)
                    else:
                        # Add single file to tar
                        tar.add(src_path, arcname=Path(dst_path).name)

                # Read tar file content
                with tar_path.open("rb") as f:
                    data = f.read()

                # Upload to container
                await asyncio.to_thread(
                    self.container.put_archive,
                    str(Path(resolved_dst).parent) or "/",
                    data,
                )

                # Verify file was created successfully
                try:
                    await self.run_command(f"test -e {resolved_dst}")
                except Exception as e:
                    raise RuntimeError(f"Failed to verify file creation: {dst_path}") from e

        except FileNotFoundError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to copy file: {e}") from e

    @staticmethod
    async def _create_tar_stream(name: str, content: bytes) -> io.BytesIO:
        """Creates a tar file stream.

        Args:
            name: Filename.
            content: File content.

        Returns:
            Tar file stream.
        """
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode="w") as tar:
            tarinfo = tarfile.TarInfo(name=name)
            tarinfo.size = len(content)
            tar.addfile(tarinfo, io.BytesIO(content))
        tar_stream.seek(0)
        return tar_stream

    @staticmethod
    async def _read_from_tar(tar_stream) -> bytes:
        """Reads file content from a tar stream.

        Args:
            tar_stream: Tar file stream.

        Returns:
            File content.

        Raises:
            RuntimeError: If read operation fails.
        """
        with tempfile.NamedTemporaryFile() as tmp:
            for chunk in tar_stream:
                tmp.write(chunk)
            tmp.seek(0)

            with tarfile.open(fileobj=tmp) as tar:
                member = tar.next()
                if not member:
                    raise RuntimeError("Empty tar archive")

                file_content = tar.extractfile(member)
                if not file_content:
                    raise RuntimeError("Failed to extract file content")

                return file_content.read()

    async def cleanup(self) -> None:
        """Cleans up sandbox resources."""
        errors = []
        try:
            if self.terminal:
                try:
                    await self.terminal.close()
                except Exception as e:
                    errors.append(f"Terminal cleanup error: {e}")
                finally:
                    self.terminal = None

            if self.container:
                try:
                    await asyncio.to_thread(self.container.stop, timeout=5)
                except Exception as e:
                    errors.append(f"Container stop error: {e}")

                try:
                    await asyncio.to_thread(self.container.remove, force=True)
                except Exception as e:
                    errors.append(f"Container remove error: {e}")
                finally:
                    self.container = None

        except Exception as e:
            errors.append(f"General cleanup error: {e}")

        if errors:
            print(f"Warning: Errors during cleanup: {', '.join(errors)}")

    async def __aenter__(self) -> "DockerSandbox":
        """Async context manager entry."""
        return await self.create()

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.cleanup()
