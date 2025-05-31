# ...existing code...


class Settings(BaseSettings):
    # ...existing code...

    # TTS Configuration
    elevenlabs_api_key: Optional[str] = None
    podcast_host_1_voice_id: str = "default"
    podcast_host_2_voice_id: str = "default"
    podcast_output_dir: str = "output/podcasts"

    # Code Execution Settings
    code_execution_enabled: bool = True
    code_execution_timeout: int = 30
    code_execution_memory_limit: int = 100  # MB
    code_execution_max_output: int = 10000  # characters
    code_execution_allowed_languages: List[str] = ["python", "javascript"]
    code_execution_restricted_python: bool = True

    # Tool Execution & Sandboxing Settings
    tool_execution_timeout: int = 30
    tool_sandbox_enabled: bool = True
    tool_sandbox_memory_limit: str = "128m"
    tool_sandbox_cpu_limit: float = 0.5
    tool_sandbox_network_disabled: bool = True
    tool_force_sandbox_unsafe: bool = True

    # ...existing code...
