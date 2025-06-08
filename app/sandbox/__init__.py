"""
Docker Sandbox Module

Provides secure containerized execution environment with resource limits
and isolation for running untrusted code.
"""

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

__all__ = [
    "BaseSandboxClient",
    "DockerSandbox",
    "LocalSandboxClient",
    "SandboxError",
    "SandboxManager",
    "SandboxResourceError",
    "SandboxTimeoutError",
    "create_sandbox_client",
]
