"""
Configuration Migration Module

This module provides backward compatibility and migration utilities
for transitioning from the old configuration system to the new centralized one.
"""

import warnings

from app.core.settings import (
    BrowserSettings,
    KnowledgeSettings,
    LLMSettings,
    MCPSettings,
    SandboxSettings,
    SearchSettings,
)
from app.core.settings import settings as new_settings


class ConfigurationMigration:
    """Provides backward compatibility for the old configuration system."""

    def __init__(self):
        self._warned_deprecations = set()

    def _warn_deprecation(self, old_path: str, new_path: str):
        """Issue a deprecation warning once per path."""
        if old_path not in self._warned_deprecations:
            warnings.warn(
                f"Accessing configuration via '{old_path}' is deprecated. "
                f"Use '{new_path}' instead.",
                DeprecationWarning,
                stacklevel=3,
            )
            self._warned_deprecations.add(old_path)

    @property
    def llm(self) -> dict[str, LLMSettings]:
        """Backward compatibility for config.llm access."""
        self._warn_deprecation(
            "from app.config import config; config.llm",
            "from app.core.settings import settings; settings.llm_configs",
        )
        return new_settings.llm_configs

    @property
    def sandbox(self) -> SandboxSettings:
        """Backward compatibility for config.sandbox access."""
        self._warn_deprecation(
            "from app.config import config; config.sandbox",
            "from app.core.settings import settings; settings.sandbox_config",
        )
        return new_settings.sandbox_config

    @property
    def browser_config(self) -> BrowserSettings | None:
        """Backward compatibility for config.browser_config access."""
        self._warn_deprecation(
            "from app.config import config; config.browser_config",
            "from app.core.settings import settings; settings.browser_config",
        )
        return new_settings.browser_config

    @property
    def search_config(self) -> SearchSettings | None:
        """Backward compatibility for config.search_config access."""
        self._warn_deprecation(
            "from app.config import config; config.search_config",
            "from app.core.settings import settings; settings.search_config",
        )
        return new_settings.search_config

    @property
    def mcp_config(self) -> MCPSettings:
        """Backward compatibility for config.mcp_config access."""
        self._warn_deprecation(
            "from app.config import config; config.mcp_config",
            "from app.core.settings import settings; settings.mcp_config",
        )
        return new_settings.mcp_config

    @property
    def knowledge_config(self) -> KnowledgeSettings:
        """Backward compatibility for config.knowledge_config access."""
        self._warn_deprecation(
            "from app.config import config; config.knowledge_config",
            "from app.core.settings import settings; settings.knowledge_config",
        )
        return new_settings.knowledge_config

    @property
    def workspace_root(self):
        """Backward compatibility for config.workspace_root access."""
        self._warn_deprecation(
            "from app.config import config; config.workspace_root",
            "from app.core.settings import settings; settings.workspace_root",
        )
        return new_settings.workspace_root

    @property
    def root_path(self):
        """Backward compatibility for config.root_path access."""
        self._warn_deprecation(
            "from app.config import config; config.root_path",
            "from app.core.settings import settings; settings.project_root",
        )
        return new_settings.project_root


# Global backward compatibility instance
migration_config = ConfigurationMigration()
