"""
Centralized logger with colors to use in all scripts.
Usage: from logger_config import get_logger
"""

import logging
import sys
from typing import ClassVar


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GRAY = "\033[90m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    BRIGHT_RED = "\033[91m"


class ColoredFormatter(logging.Formatter):
    """Formatter that adds ANSI colors by log level and highlights keywords."""

    LEVEL_COLORS: ClassVar[dict[int, str]] = {
        logging.DEBUG: Colors.CYAN,
        logging.INFO: Colors.GREEN,
        logging.WARNING: Colors.YELLOW,
        logging.ERROR: Colors.RED,
        logging.CRITICAL: Colors.BRIGHT_RED + Colors.BOLD,
    }

    KEYWORDS: ClassVar[dict[str, str]] = {
        "SUCCESS": Colors.GREEN,
        "SUCCESSFULLY": Colors.GREEN,
        "FAILED": Colors.RED,
        "ERROR": Colors.RED,
        "WARNING": Colors.YELLOW,
    }

    def format(self, record: logging.LogRecord) -> str:
        original_levelname = record.levelname
        original_msg = record.msg

        level_color = self.LEVEL_COLORS.get(record.levelno, Colors.RESET)
        record.levelname = f"{level_color}{record.levelname}{Colors.RESET}"
        record.msg = self._highlight_keywords(str(record.msg))

        msg = super().format(record)

        record.levelname = original_levelname
        record.msg = original_msg

        # Dim the timestamp and logger name
        msg = msg.replace(record.asctime, f"{Colors.GRAY}{record.asctime}{Colors.RESET}", 1)
        msg = msg.replace(record.name, f"{Colors.GRAY}{record.name}{Colors.RESET}", 1)

        return msg

    def _highlight_keywords(self, msg: str) -> str:
        # Sort by length descending so "SUCCESSFULLY" matches before "SUCCESS"
        pairs = sorted(self.KEYWORDS.items(), key=lambda kv: len(kv[0]), reverse=True)
        placeholders: dict[str, str] = {}
        for i, (word, color) in enumerate(pairs):
            if word in msg:
                placeholder = f"\x00{i}\x00"
                msg = msg.replace(word, placeholder)
                placeholders[placeholder] = f"{color}{word}{Colors.RESET}"
        for placeholder, colored in placeholders.items():
            msg = msg.replace(placeholder, colored)
        return msg


_FORMATTER = ColoredFormatter(
    fmt="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)

_PLAIN_FORMATTER = logging.Formatter(
    fmt="%(asctime)s %(name)s %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def _build_console_handler(level: int) -> logging.StreamHandler:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(_FORMATTER)
    return handler


def _build_file_handler(log_file: str, level: int) -> logging.FileHandler:
    handler = logging.FileHandler(log_file)
    handler.setLevel(level)
    handler.setFormatter(_PLAIN_FORMATTER)
    return handler


def _configure(name: str, level: int, *handlers: logging.Handler) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(level)
    for handler in handlers:
        logger.addHandler(handler)
    return logger


def get_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Returns a colored console logger.

    Args:
        name:  Logger name, typically ``__name__``.
        level: Logging level (default: INFO).
    """
    return _configure(name, level, _build_console_handler(level))


def get_file_logger(name: str, log_file: str, level: int = logging.INFO) -> logging.Logger:
    """
    Returns a logger that writes colored output to console and plain text to a file.

    Args:
        name:     Logger name, typically ``__name__``.
        log_file: Path to the log file.
        level:    Logging level (default: INFO).
    """
    return _configure(
        name,
        level,
        _build_console_handler(level),
        _build_file_handler(log_file, level),
    )
