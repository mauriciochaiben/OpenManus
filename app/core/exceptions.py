"""Core exceptions for the application."""


class OpenManusError(Exception):
    """Base exception for all OpenManus errors"""


class ValidationError(OpenManusError):
    """Exception raised for validation errors"""


class ConfigurationError(OpenManusError):
    """Exception raised for configuration errors"""


class ProcessingError(OpenManusError):
    """Exception raised for processing errors"""


class ToolError(OpenManusError):
    """Raised when a tool encounters an error."""

    def __init__(self, message):
        self.message = message


class TokenLimitExceeded(OpenManusError):
    """Exception raised when the token limit is exceeded"""