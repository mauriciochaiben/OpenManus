"""
DEPRECATED: Legacy configuration module.

This module is deprecated and will be removed in a future version.
Please use the new centralized configuration system:

    from app.core.settings import settings

For backward compatibility, the old 'config' object is still available
but will issue deprecation warnings.
"""

import warnings
from app.core.config_migration import migration_config

# Issue deprecation warning when this module is imported
warnings.warn(
    "app.config is deprecated. Use 'from app.core.settings import settings' instead.",
    DeprecationWarning,
    stacklevel=2
)

# Maintain backward compatibility
config = migration_config
