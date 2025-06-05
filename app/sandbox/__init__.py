"""
Docker Sandbox Module

Provides secure containerized execution environment with resource limits
and isolation for running untrusted code.
"""

try:
    from app.sandbox.client import (
        BaseSandboxClient,
        LocalSandboxClient,
        create_sandbox_client,
    )
    from app.sandbox.core.exceptions import (
        SandboxError,
        SandboxResourceError,
        SandboxTimeoutError,
    )
    from app.sandbox.core.manager import SandboxManager
    from app.sandbox.core.sandbox import DockerSandbox
except Exception:  # pragma: no cover - optional dependency missing
    BaseSandboxClient = LocalSandboxClient = SandboxManager = DockerSandbox = None
    SandboxError = SandboxResourceError = SandboxTimeoutError = Exception
    def create_sandbox_client(*_args, **_kwargs):
        raise ImportError("docker is required for sandbox functionality")

__all__ = [
    "DockerSandbox",
    "SandboxManager",
    "BaseSandboxClient",
    "LocalSandboxClient",
    "create_sandbox_client",
    "SandboxError",
    "SandboxTimeoutError",
    "SandboxResourceError",
]
