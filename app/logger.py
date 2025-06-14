from datetime import datetime
import logging
import sys

try:
    from loguru import logger as _logger  # type: ignore
except Exception:  # pragma: no cover - optional dependency missing
    _logger = logging.getLogger("openmanus")

from app.core.settings import settings

_print_level = "INFO"


def define_log_level(print_level="INFO", logfile_level="DEBUG", name: str | None = None):
    """Adjust the log level to above level"""
    global _print_level  # noqa: PLW0603
    _print_level = print_level

    current_date = datetime.now()
    formatted_date = current_date.strftime("%Y%m%d%H%M%S")
    log_name = f"{name}_{formatted_date}" if name else formatted_date  # name a log with prefix name

    if hasattr(_logger, "remove"):
        _logger.remove()
        _logger.add(sys.stderr, level=print_level)
        _logger.add(settings.project_root / f"logs/{log_name}.log", level=logfile_level)
    else:  # Basic logging fallback
        _logger.setLevel(print_level)
        handler = logging.StreamHandler(sys.stderr)
        handler.setLevel(print_level)
        _logger.addHandler(handler)
    return _logger


logger = define_log_level()


if __name__ == "__main__":
    logger.info("Starting application")
    logger.debug("Debug message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")

    try:
        raise ValueError("Test error")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
