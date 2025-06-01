"""
DEPRECATED: This configuration module is deprecated.

Please use the new centralized configuration system:
    from app.core.settings import settings

This module will be removed in a future version.
"""

import warnings
from typing import Optional, List

# Import the new settings system
from app.core.settings import settings as new_settings

# Issue deprecation warning
warnings.warn(
    "app.core.config is deprecated. Use 'from app.core.settings import settings' instead.",
    DeprecationWarning,
    stacklevel=2
)


class DeprecatedSettings:
    """Backward compatibility wrapper for the old Settings class."""
    
    def __getattr__(self, name: str):
        """Proxy attribute access to the new settings."""
        warnings.warn(
            f"Accessing settings.{name} from app.core.config is deprecated. "
            f"Use 'from app.core.settings import settings; settings.{name}' instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return getattr(new_settings, name)


# Maintain backward compatibility
settings = DeprecatedSettings()
