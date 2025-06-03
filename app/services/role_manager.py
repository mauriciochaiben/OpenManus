"""
Role Manager Service

Manages role configurations and provides agent instances based on role names.
Supports loading configurations from YAML files or database sources.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import yaml

from app.infrastructure.messaging.event_bus import EventBus
from app.roles.planner_agent import PlannerAgent
from app.roles.tool_user_agent import ToolUserAgent

logger = logging.getLogger(__name__)


class RoleConfigLoader(ABC):
    """Abstract base class for role configuration loaders."""

    @abstractmethod
    async def load_role_config(self, role_name: str) -> dict[str, Any] | None:
        """Load configuration for a specific role."""
        pass

    @abstractmethod
    async def load_all_roles(self) -> dict[str, dict[str, Any]]:
        """Load all available role configurations."""
        pass


class YamlRoleConfigLoader(RoleConfigLoader):
    """Loads role configurations from YAML files."""

    def __init__(self, config_dir: str | Path = "app/config/roles"):
        """
        Initialize the YAML config loader.

        Args:
            config_dir: Directory containing role configuration YAML files
        """
        self.config_dir = Path(config_dir)
        self._role_cache: dict[str, dict[str, Any]] = {}
        self._cache_loaded = False

    async def load_role_config(self, role_name: str) -> dict[str, Any] | None:
        """
        Load configuration for a specific role from YAML file.

        Args:
            role_name: Name of the role to load

        Returns:
            Role configuration dictionary or None if not found
        """
        if not self._cache_loaded:
            await self._load_cache()

        return self._role_cache.get(role_name)

    async def load_all_roles(self) -> dict[str, dict[str, Any]]:
        """
        Load all available role configurations from YAML files.

        Returns:
            Dictionary mapping role names to their configurations
        """
        if not self._cache_loaded:
            await self._load_cache()

        return self._role_cache.copy()

    async def _load_cache(self):
        """Load all role configurations into cache."""
        try:
            self._role_cache.clear()

            if not self.config_dir.exists():
                logger.warning(f"Role config directory does not exist: {self.config_dir}")
                self._cache_loaded = True
                return

            # Load individual role files
            for yaml_file in self.config_dir.glob("*.yaml"):
                try:
                    with yaml_file.open(encoding="utf-8") as f:
                        config = yaml.safe_load(f)

                    if config and isinstance(config, dict):
                        role_name = yaml_file.stem
                        self._role_cache[role_name] = config
                        logger.debug(f"Loaded role config: {role_name}")

                except Exception as e:
                    logger.error(f"Error loading role config from {yaml_file}: {str(e)}")

            # Also try to load from a single roles.yaml file
            roles_file = self.config_dir / "roles.yaml"
            if roles_file.exists():
                try:
                    with roles_file.open(encoding="utf-8") as f:
                        all_roles = yaml.safe_load(f)

                    if all_roles and isinstance(all_roles, dict):
                        self._role_cache.update(all_roles)
                        logger.debug(f"Loaded roles from unified config: {list(all_roles.keys())}")

                except Exception as e:
                    logger.error(f"Error loading unified roles config: {str(e)}")

            self._cache_loaded = True
            logger.info(f"Loaded {len(self._role_cache)} role configurations")

        except Exception as e:
            logger.error(f"Error loading role cache: {str(e)}")
            self._cache_loaded = True


class DatabaseRoleConfigLoader(RoleConfigLoader):
    """Loads role configurations from database."""

    def __init__(self, db_session=None):
        """
        Initialize the database config loader.

        Args:
            db_session: Database session for querying role configurations
        """
        self.db_session = db_session

    async def load_role_config(self, role_name: str) -> dict[str, Any] | None:  # noqa: ARG002
        """
        Load configuration for a specific role from database.

        Args:
            role_name: Name of the role to load

        Returns:
            Role configuration dictionary or None if not found
        """
        # TODO: Implement database loading when database models are ready
        logger.warning("Database role loading not yet implemented")
        return None

    async def load_all_roles(self) -> dict[str, dict[str, Any]]:
        """
        Load all available role configurations from database.

        Returns:
            Dictionary mapping role names to their configurations
        """
        # TODO: Implement database loading when database models are ready
        logger.warning("Database role loading not yet implemented")
        return {}


class RoleManager:
    """
    Manages role configurations and provides agent instances.

    This class handles loading role configurations from various sources
    and instantiating appropriate agent classes based on role specifications.
    """

    # Registry of available agent classes
    AGENT_REGISTRY: dict[str, type] = {
        "planner": PlannerAgent,
        "tool_user": ToolUserAgent,
        "planner_agent": PlannerAgent,
        "tool_user_agent": ToolUserAgent,
    }

    def __init__(self, config_loader: RoleConfigLoader, event_bus: EventBus | None = None):
        """
        Initialize the role manager.

        Args:
            config_loader: Configuration loader instance
            event_bus: Optional event bus for agent communication
        """
        self.config_loader = config_loader
        self.event_bus = event_bus
        self._role_instances: dict[str, Any] = {}
        self._role_configs: dict[str, dict[str, Any]] = {}

    async def get_agent(self, role_name: str, **kwargs) -> Any | None:
        """
        Get an agent instance for the specified role.

        Args:
            role_name: Name of the role to instantiate
            **kwargs: Additional arguments to pass to agent constructor

        Returns:
            Agent instance or None if role not found
        """
        try:
            # Check if we already have an instance (singleton pattern)
            if role_name in self._role_instances:
                return self._role_instances[role_name]

            # Load role configuration
            role_config = await self._get_role_config(role_name)
            if not role_config:
                logger.error(f"Role configuration not found: {role_name}")
                return None

            # Create agent instance
            agent = await self._create_agent_instance(role_name, role_config, **kwargs)
            if agent:
                # Cache the instance
                self._role_instances[role_name] = agent
                logger.info(f"Created agent instance for role: {role_name}")

            return agent

        except Exception as e:
            logger.error(f"Error getting agent for role '{role_name}': {str(e)}")
            return None

    async def get_available_roles(self) -> dict[str, dict[str, Any]]:
        """
        Get all available role configurations.

        Returns:
            Dictionary mapping role names to their configurations
        """
        try:
            return await self.config_loader.load_all_roles()
        except Exception as e:
            logger.error(f"Error loading available roles: {str(e)}")
            return {}

    async def register_agent_class(self, agent_type: str, agent_class: type):
        """
        Register a new agent class in the registry.

        Args:
            agent_type: Type identifier for the agent
            agent_class: Agent class to register
        """
        self.AGENT_REGISTRY[agent_type] = agent_class
        logger.info(f"Registered agent class: {agent_type} -> {agent_class.__name__}")

    async def reload_role_config(self, role_name: str):
        """
        Reload configuration for a specific role and recreate instance.

        Args:
            role_name: Name of the role to reload
        """
        try:
            # Remove cached instance
            if role_name in self._role_instances:
                del self._role_instances[role_name]

            # Remove cached config
            if role_name in self._role_configs:
                del self._role_configs[role_name]

            # Force reload from source
            role_config = await self.config_loader.load_role_config(role_name)
            if role_config:
                self._role_configs[role_name] = role_config
                logger.info(f"Reloaded configuration for role: {role_name}")

        except Exception as e:
            logger.error(f"Error reloading role config for '{role_name}': {str(e)}")

    async def _get_role_config(self, role_name: str) -> dict[str, Any] | None:
        """Get role configuration with caching."""
        if role_name not in self._role_configs:
            config = await self.config_loader.load_role_config(role_name)
            if config:
                self._role_configs[role_name] = config

        return self._role_configs.get(role_name)

    async def _create_agent_instance(self, role_name: str, role_config: dict[str, Any], **kwargs) -> Any | None:
        """
        Create an agent instance based on role configuration.

        Args:
            role_name: Name of the role
            role_config: Role configuration dictionary
            **kwargs: Additional constructor arguments

        Returns:
            Agent instance or None if creation fails
        """
        try:
            # Get agent type from config
            agent_type = role_config.get("agent_type", role_name)

            # Look up agent class
            agent_class = self.AGENT_REGISTRY.get(agent_type)
            if not agent_class:
                logger.error(f"Unknown agent type: {agent_type}")
                return None

            # Prepare constructor arguments
            constructor_args = {"role_name": role_name, "config": role_config, **kwargs}

            # Add event bus if available
            if self.event_bus:
                constructor_args["event_bus"] = self.event_bus

            # Add any additional config parameters
            agent_config = role_config.get("agent_config", {})
            constructor_args.update(agent_config)

            # Create instance
            agent = agent_class(**constructor_args)

            # Initialize if the agent has an init method
            if hasattr(agent, "initialize") and callable(agent.initialize):
                await agent.initialize()

            return agent

        except Exception as e:
            logger.error(f"Error creating agent instance for role '{role_name}': {str(e)}")
            return None

    def clear_cache(self):
        """Clear all cached instances and configurations."""
        self._role_instances.clear()
        self._role_configs.clear()
        logger.info("Cleared role manager cache")


# Factory functions for common use cases


def create_yaml_role_manager(
    config_dir: str | Path = "app/config/roles",
    event_bus: EventBus | None = None,
) -> RoleManager:
    """
    Create a role manager with YAML configuration loader.

    Args:
        config_dir: Directory containing YAML role configurations
        event_bus: Optional event bus for agent communication

    Returns:
        Configured RoleManager instance
    """
    config_loader = YamlRoleConfigLoader(config_dir)
    return RoleManager(config_loader, event_bus)


def create_database_role_manager(db_session=None, event_bus: EventBus | None = None) -> RoleManager:
    """
    Create a role manager with database configuration loader.

    Args:
        db_session: Database session for configuration queries
        event_bus: Optional event bus for agent communication

    Returns:
        Configured RoleManager instance
    """
    config_loader = DatabaseRoleConfigLoader(db_session)
    return RoleManager(config_loader, event_bus)


# Default role configurations for fallback
DEFAULT_ROLES = {
    "planner": {
        "agent_type": "planner",
        "description": "AI agent specialized in planning and task decomposition",
        "capabilities": ["planning", "task_breakdown", "strategy_development"],
        "agent_config": {"max_planning_depth": 5, "use_context_enhancement": True},
    },
    "tool_user": {
        "agent_type": "tool_user",
        "description": "AI agent specialized in using tools and executing tasks",
        "capabilities": ["tool_usage", "task_execution", "file_operations"],
        "agent_config": {"max_tool_calls": 10, "timeout_seconds": 300},
    },
    "researcher": {
        "agent_type": "planner",
        "description": "AI agent specialized in research and information gathering",
        "capabilities": ["research", "information_gathering", "analysis"],
        "agent_config": {
            "research_depth": "comprehensive",
            "use_context_enhancement": True,
            "max_sources": 10,
        },
    },
}
