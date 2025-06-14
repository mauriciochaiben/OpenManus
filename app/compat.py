"""Compatibility utilities for optional dependencies and Pydantic versions."""

try:  # Pydantic v2 provides these APIs
    from pydantic import BaseModel, Field, computed_field, field_validator, model_validator
except ImportError:  # fall back to Pydantic v1
    from pydantic import BaseModel, Field, root_validator, validator

    def field_validator(*fields, **kwargs):
        return validator(*fields, **kwargs)

    def computed_field(*_args, **_kwargs):  # very small substitute
        def decorator(func):
            return property(func)

        return decorator

    def model_validator(*args, **kwargs):
        """Fallback implementation using :func:`root_validator`."""
        return root_validator(*args, **kwargs)


__all__ = [
    "BaseModel",
    "Field",
    "computed_field",
    "field_validator",
    "model_validator",
]
