import asyncio
import logging
import os
from typing import ClassVar

from app.exceptions import ToolError
from app.tool.base import BaseTool, CLIResult

logger = logging.getLogger(__name__)

_BASH_DESCRIPTION = """Execute a bash command in the terminal.
* Long running commands: For commands that may run indefinitely, it should be run in the background and the output should be redirected to a file, e.g. command = `python3 app.py > server.log 2>&1 &`.
* Interactive: If a bash command returns exit code `-1`, this means the process is not yet finished. The assistant must then send a second call to terminal with an empty `command` (which will retrieve any additional logs), or it can send additional text (set `command` to the text) to STDIN of the running process, or it can send command=`ctrl+c` to interrupt the process.
* Timeout: If a command execution result says "Command timed out. Sending SIGINT to the process", the assistant should retry running the command in the background.
"""


class _BashSession:
    """A session of a bash shell."""

    _started: bool
    _process: asyncio.subprocess.Process | None

    command: str = "/bin/bash"
    _output_delay: float = 0.2  # seconds
    _timeout: float = 120.0  # seconds
    _sentinel: str = "<<exit>>"

    def __init__(self):
        self._started = False
        self._timed_out = False
        self._process = None

    async def start(self):
        if self._started:
            return

        self._process = await asyncio.create_subprocess_exec(
            "/bin/bash",
            "-i",
            preexec_fn=os.setsid,
            bufsize=0,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        self._started = True

    def stop(self):
        """Terminate the bash shell."""
        if not self._started:
            raise ToolError("Session has not started.")
        if not self._process or self._process.returncode is not None:
            return
        self._process.terminate()

    async def _read_until_sentinel(self, stream: asyncio.StreamReader) -> str:
        """Read from stream until sentinel is found."""
        output_parts = []
        while True:
            try:
                # Read available data
                data = await asyncio.wait_for(stream.read(4096), timeout=self._output_delay)
                if not data:
                    break

                text = data.decode("utf-8", errors="replace")
                output_parts.append(text)

                # Check if we have the sentinel
                full_output = "".join(output_parts)
                if self._sentinel in full_output:
                    # Return everything before the sentinel
                    return full_output[: full_output.index(self._sentinel)]

            except TimeoutError:
                # No more immediate data, check what we have
                full_output = "".join(output_parts)
                if self._sentinel in full_output:
                    return full_output[: full_output.index(self._sentinel)]
                # Continue reading if no sentinel found
                continue

        return "".join(output_parts)

    async def run(self, command: str):
        """Execute a command in the bash shell."""
        if not self._started:
            raise ToolError("Session has not started.")
        if not self._process or self._process.returncode is not None:
            return CLIResult(
                system="tool must be restarted",
                error=f"bash has exited with returncode {self._process.returncode if self._process else 'unknown'}",
            )
        if self._timed_out:
            raise ToolError(
                f"timed out: bash has not returned in {self._timeout} seconds and must be restarted",
            )

        # Validate process streams
        if not self._process.stdin:
            raise RuntimeError("Process stdin is not available")
        if not self._process.stdout:
            raise RuntimeError("Process stdout is not available")
        if not self._process.stderr:
            raise RuntimeError("Process stderr is not available")

        # Send command to the process
        command_with_sentinel = f"{command}; echo '{self._sentinel}'\n"
        self._process.stdin.write(command_with_sentinel.encode())
        await self._process.stdin.drain()

        # Read output with timeout
        try:
            async with asyncio.timeout(self._timeout):
                output = await self._read_until_sentinel(self._process.stdout)

                # Read any stderr data that's immediately available
                error_parts = []
                try:
                    while True:
                        error_data = await asyncio.wait_for(self._process.stderr.read(4096), timeout=0.1)
                        if not error_data:
                            break
                        error_parts.append(error_data.decode("utf-8", errors="replace"))
                except TimeoutError:
                    pass  # No more stderr data available

                error = "".join(error_parts)

        except TimeoutError:
            self._timed_out = True
            raise ToolError(
                f"timed out: bash has not returned in {self._timeout} seconds and must be restarted",
            ) from None

        # Clean up output
        if output.endswith("\n"):
            output = output[:-1]
        if error.endswith("\n"):
            error = error[:-1]

        return CLIResult(output=output, error=error)


class Bash(BaseTool):
    """A tool for executing bash commands"""

    name: str = "bash"
    description: str = _BASH_DESCRIPTION
    parameters: ClassVar[dict] = {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The bash command to execute. Can be empty to view additional logs when previous exit code is `-1`. Can be `ctrl+c` to interrupt the currently running process.",
            },
        },
        "required": ["command"],
    }

    _session: _BashSession | None = None

    async def execute(
        self,
        command: str | None = None,
        restart: bool = False,
        **kwargs,  # noqa: ARG002
    ) -> CLIResult:
        if restart:
            if self._session:
                self._session.stop()
            self._session = _BashSession()
            await self._session.start()

            return CLIResult(system="tool has been restarted.")

        if self._session is None:
            self._session = _BashSession()
            await self._session.start()

        if command is not None:
            return await self._session.run(command)

        raise ToolError("no command provided.")


if __name__ == "__main__":
    bash = Bash()
    rst = asyncio.run(bash.execute("ls -l"))
    print(rst)
